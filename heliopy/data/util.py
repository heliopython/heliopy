"""
Utility functions for data downloading.

**Note**: these methods are liable to change at any time.
"""
import abc
import collections as coll
import datetime as dt
import io
import logging
import os
import pathlib as path
import re
import shutil
import sys
import urllib.error as urlerror
import urllib.request as urlreq
import warnings

import astropy.units as u
import cdflib
import dateutil.relativedelta as reldelt
import numpy as np
import pandas as pd
import requests
import sunpy.time
import sunpy.timeseries as ts

import heliopy.data.helper as helper
from heliopy import config

data_dir = path.Path(config['download_dir'])
logger = logging.getLogger(__name__)


def _load_raw_file(raw_file, processing_func, processing_kwargs):
    if not raw_file.exists():
        return
    # Convert raw file to a dataframe
    logger.info('Loading {}'.format(raw_file))
    try:
        file = _load_local(raw_file)
        df = processing_func(file, **processing_kwargs)
        if use_hdf:
            _save_hdf(df, raw_file)
        if isinstance(file, io.IOBase) and not file.closed:
            file.close()
        return df
    except NoDataError:
        return


class NoDataError(RuntimeError):
    pass


def units_attach(data, units, warn_missing_units=True):
    """
    Takes the units defined by the user and attaches them to the TimeSeries.

    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        Input data. Takes the DataFrame which needs to have units attached.
    units : :class:`collections.OrderedDict`
        The units manually defined by the user.

    Returns
    -------
    out : :class:`~sunpy.timeseries.GenericTimeSeries`
        DataFrame converted into TimeSeries with units attached.
    """
    missing_msg = ('If you are trying to auomatically download data '
                   'with HelioPy this is a bug, please report it at '
                   'https://github.com/heliopython/heliopy/issues')
    unit_keys = list(units.keys())
    missing_names = []
    for column_name in data.columns:
        if column_name not in unit_keys:
            units[column_name] = u.dimensionless_unscaled
            missing_names.append(column_name)

    if warn_missing_units and len(missing_names):
        missing_names = '[' + ", ".join(missing_names) + ']'
        message = (f"{missing_names} columns have missing units."
                   f"\n{missing_msg}")
        warnings.warn(message, Warning)

    timeseries_data = ts.GenericTimeSeries(data, units=units)
    return timeseries_data


def cdf_units(cdf_, manual_units=None, length=None):
    """
    Takes the CDF File and the required keys, and finds the units of the
    selected keys.

    Parameters
    ----------
    cdf_ : cdflib.cdfread.CDF
        Opened cdf file
    manual_units : ~collections.OrderedDict
        Manually defined units to be attached to the data that will be
        returned.

    Returns
    -------
    out : :class:`collections.OrderedDict`
        Returns an OrderedDict with units of the selected keys.
    """
    units = coll.OrderedDict()

    # Get the list of all variables
    var_list = _get_cdf_vars(cdf_)
    logger.info(f'Found the following variables in CDF: {var_list}')
    # Get a mapping from each key to any sub-keys
    key_dict = {}
    # Extract the list of valid keys in the zVar or rVar
    for key in var_list:
        y = np.array(cdf_.varget(key))
        ncols = y.shape
        if len(ncols) == 1:
            key_dict[key] = key
        if len(ncols) > 1:
            val = []
            val.append(key)
            for x in range(0, ncols[1]):
                field = f'{key}_{x}'
                val.append(field)
            key_dict[key] = val

    logger.info(f'Getting units for {key_dict}')
    # Assigning units to the keys
    for key, val in key_dict.items():
        unit_str = None
        temp_unit = None
        # Try to get a unit string from the CDF file
        try:
            unit_str = cdf_.varattsget(key)['UNITS']
            # Try and convert to an astropy unit
            try:
                temp_unit = u.Unit(unit_str)
            except (TypeError, ValueError):
                if manual_units and key in manual_units:
                    temp_unit = manual_units[key]
                elif helper.cdf_dict(unit_str) is not None:
                    temp_unit = helper.cdf_dict(unit_str)

                if temp_unit is None:
                    message = (f"The CDF provided units ('{unit_str}') for"
                               f" key '{key}' are unknown")
                    warnings.warn(message)
                    continue
        # Fallback on user provided units
        except KeyError:
            if manual_units and key in manual_units:
                temp_unit = manual_units[key]
            else:
                temp_unit = u.dimensionless_unscaled

        if isinstance(val, list):
            for v in val:
                units[v] = temp_unit
        else:
            units[val] = temp_unit

    if manual_units:
        units.update(manual_units)
    logger.info(f'Extracted following units: {units}')
    return units


def timefilter(data, starttime, endtime):
    """
    Puts data in a single dataframe, and filters it between times.

    Parameters
    ----------
    data : :class:`pandas.DataFrame` or list
        Input data. If a list, ``pd.concat(data)`` will be run to put it in
        a DataFrame.
    starttime : datetime.datetime
        Start of interval.
    endtime : datetime.datetime
        End of interval.

    Returns
    -------
    out : :class:`pandas.DataFrame`
        Filtered data.
    """
    if len(data) == 0:
        raise RuntimeError(
            'No data available between {} and {}'.format(starttime, endtime))
    if isinstance(data, list):
        data = pd.concat(data)
    # Get time values
    if 'Time' in data.columns:
        time = data['Time']
    elif 'Time' in data.index.names:
        time = data.index.get_level_values('Time')
    else:
        raise KeyError('The label "Time" was not found in '
                       'the dataframe columns or index')

    data = data[(time > starttime) &
                (time < endtime)]
    # Assume if this fails we have a multi-index that already has time in it
    if ('Time' in data.columns) and (len(data.index.shape) == 1):
        data = data.set_index('Time', drop=True)

    return data


def cdf2df(cdf, index_key, dtimeindex=True, badvalues=None,
           ignore=None, include=None):
    """
    Converts a cdf file to a pandas dataframe.

    Note that this only works for 1 dimensional data, other data such as
    distribution functions or pitch angles will not work properly.

    Parameters
    ----------
    cdf : cdflib.cdfread.CDF
        Opened CDF file.
    index_key : str
        The CDF key to use as the index in the output DataFrame.
    dtimeindex : bool
        If ``True``, the DataFrame index is parsed as a datetime.
        Default is ``True``.
    badvalues : dict, list
        Deprecated.
    ignore : list
        In case a CDF file has columns that are unused / not required, then
        the column names can be passed as a list into the function.
    include : str, list
        If only specific columns of a CDF file are desired, then the column
        names can be passed as a list into the function. Should not be used
        with ``ignore``.

    Returns
    -------
    df : :class:`pandas.DataFrame`
        Data frame with read in data.
    """
    if badvalues is not None:
        warnings.warn('The badvalues argument is decprecated, as bad values '
                      'are now automatically recognised using the FILLVAL CDF '
                      'attribute.', DeprecationWarning)
    if include is not None:
        if ignore is not None:
            raise ValueError('ignore and include are incompatible keywords')
        if isinstance(include, str):
            include = [include]
        if index_key not in include:
            include.append(index_key)

    # Extract index values
    index_info = cdf.varinq(index_key)
    if index_info['Last_Rec'] == -1:
        raise CDFEmptyError('No records present in CDF file')

    index = cdf.varget(index_key)
    try:
        # If there are multiple indexes, take the first one
        # TODO: this is just plain wrong, there should be a way to get all
        # the indexes out
        index = index[...][:, 0]
    except IndexError:
        pass

    if dtimeindex:
        index = cdflib.epochs.CDFepoch.breakdown(index, to_np=True)
        index_df = pd.DataFrame({'year': index[:, 0],
                                 'month': index[:, 1],
                                 'day': index[:, 2],
                                 'hour': index[:, 3],
                                 'minute': index[:, 4],
                                 'second': index[:, 5],
                                 'ms': index[:, 6],
                                 })
        # Not all CDFs store pass milliseconds
        try:
            index_df['us'] = index[:, 7]
            index_df['ns'] = index[:, 8]
        except IndexError:
            pass
        index = pd.DatetimeIndex(pd.to_datetime(index_df), name='Time')
    df = pd.DataFrame(index=index)
    npoints = df.shape[0]

    var_list = _get_cdf_vars(cdf)
    keys = {}
    # Get mapping from each attr to sub-variables
    for cdf_key in var_list:
        if ignore:
            if cdf_key in ignore:
                continue
        elif include:
            if cdf_key not in include:
                continue
        if cdf_key == 'Epoch':
            keys[cdf_key] = 'Time'
        else:
            keys[cdf_key] = cdf_key
    # Remove index key, as we have already used it to create the index
    keys.pop(index_key)
    # Remove keys for data that doesn't have the right shape to load in CDF
    # Mapping of keys to variable data
    vars = {cdf_key: cdf.varget(cdf_key) for cdf_key in keys.copy()}
    for cdf_key in keys:
        var = vars[cdf_key]
        if type(var) is np.ndarray:
            key_shape = var.shape
            if len(key_shape) == 0 or key_shape[0] != npoints:
                vars.pop(cdf_key)
        else:
            vars.pop(cdf_key)

    # Loop through each key and put data into the dataframe
    for cdf_key in vars:
        df_key = keys[cdf_key]
        # Get fill value for this key
        try:
            fillval = float(cdf.varattsget(cdf_key)['FILLVAL'])
        except KeyError:
            fillval = np.nan

        if isinstance(df_key, list):
            for i, subkey in enumerate(df_key):
                data = vars[cdf_key][...][:, i]
                data = _fillval_nan(data, fillval)
                df[subkey] = data
        else:
            # If ndims is 1, we just have a single column of data
            # If ndims is 2, have multiple columns of data under same key
            key_shape = vars[cdf_key].shape
            ndims = len(key_shape)
            if ndims == 1:
                data = vars[cdf_key][...]
                data = _fillval_nan(data, fillval)
                df[df_key] = data
            elif ndims == 2:
                for i in range(key_shape[1]):
                    data = vars[cdf_key][...][:, i]
                    data = _fillval_nan(data, fillval)
                    df[f'{df_key}_{i}'] = data

    return df


def _get_cdf_vars(cdf):
    # Get list of all the variables in an open CDF file
    var_list = []
    cdf_info = cdf.cdf_info()
    for attr in list(cdf_info.keys()):
        if 'variable' in attr.lower() and len(cdf_info[attr]) > 0:
            for var in cdf_info[attr]:
                var_list += [var]

    return var_list


def _fillval_nan(data, fillval):
    try:
        data[data == fillval] = np.nan
    except ValueError:
        # This happens if we try and assign a NaN to an int type
        pass
    return data


class RemoteFileNotPresentError(RuntimeError):
    pass


class CDFEmptyError(RuntimeError):
    pass


def _load_cdf(file_path):
    '''
    A function to handle loading cdflib, and printing a nice error if things
    go wrong.
    '''
    try:
        cdf = cdflib.CDF(str(file_path))
    except Exception as err:
        print('Error whilst trying to load {}\n'.format(file_path))
        raise err
    return cdf


def _is_cdf(file_path):
    file_path = path.Path(file_path)
    if file_path.suffix == '.cdf':
        return True
    return False


def _load_local(file_path, filetype=None):
    # Import local file
    if _is_cdf(file_path):
        return _load_cdf(file_path)
    else:
        f = open(str(file_path))
        return f


def _reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = min(100, readsofar * 1e2 / totalsize)
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        # Near the end
        if readsofar >= totalsize:
            sys.stderr.write("\n")
    # Total size is unknown
    else:
        sys.stderr.write("\rRead %d" % (readsofar,))


def _checkdir(directory):
    """
    Checks if directory exists, if not creates directory.

    Parameters
    ----------
    directory : str
        Directory to check.

    Returns
    -------
    isdir : bool
        True if directory exists, False if directory didn't exist when
        function was called.
    """
    directory = path.Path(directory)
    if not directory.exists():
        print('Creating new directory', directory)
        directory.mkdir(parents=True)
        return False
    else:
        return True
