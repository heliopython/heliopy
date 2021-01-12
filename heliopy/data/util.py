"""
Utility functions for data downloading.

**Note**: these methods are liable to change at any time.
"""
import abc
import datetime as dt
import dateutil.relativedelta as reldelt
import io
import os
import logging
import pathlib as path
import requests
import re
import shutil
import sys
import urllib.error as urlerror
import urllib.request as urlreq
import astropy.units as u
import sunpy.time
import sunpy.timeseries as ts
import warnings
import collections as coll
import cdflib

import numpy as np
import pandas as pd
import heliopy.data.helper as helper

from heliopy import config
use_hdf = config['use_hdf']
data_dir = path.Path(config['download_dir'])
logger = logging.getLogger(__name__)


class Downloader(abc.ABC):
    """
    A template class, that should be sub-classed to provide methods for
    downloading a single dataset.

    The following methods must be implemented by sub-classes:

    - :meth:`Downloader.intervals()`: given a time interval, this
      method should split the interval up into sub-intervals. Each of these
      sub-intervals corresponds directly to a single file to download, store,
      and read in.
    - :meth:`Downloader.local_dir()`: given an interval, returns the
      local directory in which the file is stored.
    - :meth:`Downloader.fname()`: given an interval, returns the
      local filename in which the file is stored.
    - :meth:`Downloader.download()`: given an interval, download the data for
      that interval.
    - :meth:`Downloader.load_local_file()`: given an interval, load the local
      file and return a :class:`pandas.DataFrame` object containing the data.

    Attributes
    ----------
    units : dict
    """
    def load(self, starttime, endtime):
        """
        Load all data between *starttime* and *endtime*.
        """
        data = []
        intervals = self.intervals(starttime, endtime)
        if not len(intervals):
            raise RuntimeError('No intervals provided')
        for interval in self.intervals(starttime, endtime):
            hdf_path = self.local_hdf_path(interval)
            local_path = self.local_path(interval)

            # Try to load HDF file
            if hdf_path.exists():
                data.append(pd.read_hdf(hdf_path))
                # Store the local path if loading data was successful
                local_path_successful = local_path
                continue

            # Try to load original file
            if not local_path.exists():
                # Try to download file
                try:
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    dl_path = self.download(interval)
                    if dl_path is not None and dl_path != local_path:
                        shutil.copy(dl_path, local_path)
                        os.remove(dl_path)
                except NoDataError:
                    continue

            try:
                data.append(self.load_local_file(interval))
            except CDFEmptyError:
                continue
            local_path_successful = local_path
            if use_hdf:
                data[-1].to_hdf(hdf_path, 'data', mode='w', format='f')

        # Loaded all the data, now filter between times
        data = timefilter(data, starttime, endtime)
        data = data.sort_index()

        # Attach units
        if local_path.suffix == '.cdf':
            cdf = _load_local(local_path_successful)
            if not hasattr(self, 'units'):
                self.units = None
            self.units = cdf_units(cdf, manual_units=self.units)
        # Warn by default on missing units
        if not hasattr(self, 'warn_missing_units'):
            self.warn_missing_units = True
        return units_attach(
            data, self.units, warn_missing_units=self.warn_missing_units)

    def local_path(self, interval):
        """
        Absolute path to a single local file.
        """
        local_path = self.local_dir(interval) / self.fname(interval)
        return data_dir / local_path

    def local_hdf_path(self, interval):
        """
        Absolute path to a single .hdf file.
        """
        local_path = self.local_path(interval)
        return local_path.with_suffix('.hdf')

    def local_file_exists(self, interval):
        """
        Return ``True`` if the local file exists.
        """
        return self.local_path(interval).exists()

    @abc.abstractmethod
    def intervals(self, starttime, endtime):
        """
        The complete list of sub-intervals that cover a time range
        Each sub-interval is associated with a single file to be downloaded and
        read in.

        Parameters
        ----------
        starttime : datetime.datetime
        endtime : datetime.datetime

        Returns
        -------
        fnames : list of sunpy.time.TimeRange
            List of intervals
        """
        pass

    def fname(self, interval):
        """
        Return the filename to which the data is saved for a given interval.

        n.b. this does not in general have to be equal to the remote filename
        of the data.

        Parameters
        ----------
        interval : sunpy.time.TimeRange

        Returns
        -------
        fname : str
            Filename
        """
        pass

    @abc.abstractmethod
    def local_dir(self, interval):
        """
        Local directory for a given interval. This is relative to the base
        HelioPy data directory.

        Parameters
        ----------
        interval : sunpy.time.TimeRange

        Returns
        -------
        dir : pathlib.Path
            Local directory
        """
        pass

    @abc.abstractmethod
    def download(self, interval):
        """
        Download data for a given interval.

        Parameters
        ----------
        interval : sunpy.time.TimeRange

        Returns
        -------
        dl_path : pathlib.Path
            Path to the downloaded file.
        """
        pass

    @abc.abstractmethod
    def load_local_file(self, interval):
        """
        Load local file for a given interval.

        Parameters
        ----------
        interval : sunpy.time.TimeRange

        Returns
        -------
        data : pandas.DataFrame
        """
        pass

    @staticmethod
    def intervals_yearly(starttime, endtime):
        """
        Returns all annual intervals between *starttime* and *endtime*.
        """
        out = []
        # Loop through years
        for year in range(starttime.year, endtime.year + 1):
            out.append(sunpy.time.TimeRange(dt.datetime(year, 1, 1),
                                            dt.datetime(year + 1, 1, 1)))
        return out

    @staticmethod
    def intervals_monthly(starttime, endtime):
        """
        Returns all monthly intervals between *starttime* and *endtime*.
        """
        out = []
        starttime = dt.datetime(starttime.year, starttime.month, 1)
        endtime = dt.datetime(endtime.year, endtime.month, 1)
        while starttime <= endtime:
            end_month = starttime + reldelt.relativedelta(months=1)
            out.append(sunpy.time.TimeRange(starttime, end_month))
            starttime += reldelt.relativedelta(months=1)
        return out

    @staticmethod
    def intervals_daily(starttime, endtime):
        interval = sunpy.time.TimeRange(starttime, endtime)
        daylist = interval.get_dates()
        intervallist = [sunpy.time.TimeRange(t, t + dt.timedelta(days=1)) for
                        t in daylist]
        return intervallist


def process(dirs, fnames, extension, local_base_dir, remote_base_url,
            download_func, processing_func, starttime, endtime,
            try_download=True, units=None,
            processing_kwargs={}, download_info=[], remote_fnames=None,
            warn_missing_units=True):
    """
    The main utility method for systematically loading, downloading, and saving
    data.

    Parameters
    ----------
    dirs : list
        A list of directories relative to *local_base_dir*.
    fnames : list, str
        A list of filenames **without** their extension. These are the
        filenames that will be downloaded from the remote source. Must be the
        same length as *dirs*. Each filename is saved in it's respective entry
        in *dirs*. Can also be a regular expression that is used to match
        the filename (e.g. for version numbers)
    extension : str
        File extension of the raw files. **Must include leading dot**.
    local_base_dir : str
        Local base directory. ``fname[i]`` will be stored in
        ``local_base_dir / dirs[i] / fname[i] + extension``.
    remote_base_url : str
        Remote base URL. ``fname[i]`` will be downloaded from
        ``Remote / dirs[i] / fname[i] + extension``.
    download_func
        Function that takes

        - The remote base url
        - The local base directory
        - The relative directory (relative to the base url)
        - The local filename to download to
        - The remote filename
        - A file extension

        and downloads the remote file. The signature must be::

            def download_func(remote_base_url, local_base_dir,
                              directory, fname, remote_fname, extension)

        The function can also return the path of the file it downloaded,
        if this is different to the filename it is given. *download_func*
        can either silently do nothing if a given file is not available, or
        raise a `NoDataError` with a descriptive error message that will be
        printed.

    processing_func
        Function that takes an open CDF file or open plain text file,
        and returns a pandas DataFrame. The signature must be::

            def processing_func(file, **processing_kwargs)

    starttime : ~datetime.datetime
        Start of requested interval.
    endtime : ~datetime.datetime
        End of requested interval.
    try_download : bool
        If ``True``, try to download data. If ``False`` don't.
        Default is ``True``.

    units : ~collections.OrderedDict
        Manually defined units to be attached to the data that will be
        returned.

        Must map column headers (strings) to :class:`~astropy.units.Quantity`
        objects. If units are present, then a TimeSeries object is returned,
        else a Pandas DataFrame.

    processing_kwargs : dict
        Extra keyword arguments to be passed to the processing funciton.

    download_info : list
        A list with the same length as *fnames*, which contains extra info
        that is handed to *download_func* for each file individually.
    remote_fnames : list of str
        If the remote filenames are different from the desired downloaded
        filenames, this should be a list of length ``len(fnames)`` with the
        files to be downloaded. The ordering must be the same as *fnames*.
    warn_missing_units : bool
        If ``True``, warnings will be shown for each variable that does not
        have associated units.

    Returns
    -------
    :class:`~pandas.DataFrame` or :class:`~sunpy.timeseries.GenericTimeSeries`
        Requested data.
    """
    local_base_dir = path.Path(local_base_dir)
    data = []
    if download_info == []:
        download_info = [None] * len(dirs)
    if remote_fnames is None:
        remote_fnames = fnames.copy()

    if len(dirs) != len(fnames):
        raise ValueError(
            'Must have the same number of directories as filenames')
    if len(fnames) != len(remote_fnames):
        raise ValueError(
            'Must have the same number of remote filenames as filenames')

    zips = zip(dirs, fnames, remote_fnames, download_info)
    for directory, fname, remote_fname, dl_info in zips:
        local_dir = local_base_dir / directory
        local_file = local_dir / fname

        # Try to load hdf file
        hdf_fname = _file_match(local_dir, fname + '.hdf')
        if hdf_fname is not None:
            hdf_file_path = local_dir / hdf_fname
            raw_file_path = hdf_file_path.with_suffix(extension)
            logger.info('Loading {}'.format(hdf_file_path))
            data.append(pd.read_hdf(hdf_file_path))
            continue

        # Try to load raw file
        raw_fname = _file_match(local_dir, fname + extension)
        if raw_fname is not None:
            raw_file_path = local_dir / raw_fname
            logger.info('Loading {}'.format(raw_file_path))
            df = _load_raw_file(raw_file_path,
                                processing_func, processing_kwargs)
            if df is not None:
                data.append(df)
                continue

        # If we can't find local file, try downloading
        if try_download:
            _checkdir(local_dir)
            args = ()
            if dl_info is not None:
                args = (dl_info,)
            try:
                new_path = download_func(remote_base_url, local_base_dir,
                                         directory, fname, remote_fname,
                                         extension, *args)
            except NoDataError as e:
                print(str(e))
                continue
            if new_path is not None:
                shutil.copy(new_path, local_file.with_suffix(extension))

            raw_fname = _file_match(local_dir, fname + extension)
            # Print a message if file hasn't been downloaded
            if raw_fname is not None:
                raw_file_path = local_dir / raw_fname
                df = _load_raw_file(raw_file_path,
                                    processing_func, processing_kwargs)
                if df is not None:
                    data.append(df)
                continue
            else:
                logger.info('File {}{}/{}{} not available remotely\n'.format(
                            remote_base_url, directory, fname, extension))
                continue
        else:
            msg = ('File {a}/{b}{c} not available locally,\n'
                   'and "try_download" set to False')
            logger.info(msg.format(a=local_dir, b=fname, c=extension))

    # Loaded all the data, now filter between times
    data = timefilter(data, starttime, endtime)
    data = data.sort_index()

    # Attach units
    if extension == '.cdf':
        cdf = _load_local(raw_file_path)
        units = cdf_units(cdf, manual_units=units)
    return units_attach(data, units, warn_missing_units=warn_missing_units)


def _file_match(directory, fname_regex):
    """
    Check if a file in *directory* matchs the regular expression given by
    *fname_regex*. If it does, return the filename. Otherwise returns None.

    Parameters
    ----------
    directory : Path
    fname_regex : str
        Must include file extension.

    Returns
    -------
    fname : str
        Includes file extension.
    """
    if directory.exists():
        for f in directory.iterdir():
            if f.is_file():
                if re.match(fname_regex, f.name):
                    return f.name


def _save_hdf(df, raw_file):
    hdf_file = raw_file.with_suffix('.hdf')
    df.to_hdf(hdf_file, 'data', mode='w', format='f')


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
    cdf_ : cdflib.CDF
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


def pitchdist_cdf2df(cdf, distkeys, energykey, timekey, anglelabels):
    """
    Converts cdf file of a pitch angle distribution to a pandas dataframe.

    MultiIndexing is used as a pitch angle distribution is essentially a 3D
    dataset *f(time, energy, angle)*. See
    http://pandas.pydata.org/pandas-docs/stable/advanced.html#multiindex-advanced-indexing
    for more information.

    This has been constructed for importing wind swe pitch angle distributions,
    and might not generalise very well to other data sets.

    Assumes that each energy in the cdf has its own 2D array (time, angle). In
    the below description of the function there are

        - ``n`` time data points
        - ``m`` energy data points
        - ``l`` anglular data points

    Parameters
    ----------
    cdf : cdflib.CDF
        Opened cdf file.
    distkeys : list
        A list of the cdf keys for a given energies. Each array accessed by
        distkeys is shape ``(n, l)``, and there must be `m` distkeys.
    energykey : str
        The cdf key for the energy values. The array accessed by energykey
        must have shape ``(m)`` or ``(a, m)`` where ``a`` can be anything. If
        it has shape ``(a, m)``, we assume energies measured don't change, and
        take the first row as the energies for all times.
    timekey : str
        The cdf key for the timestamps. The array access by timekey must
        have shape ``(n)``
    anglelabels : list
        A list of the labels to give each anglular bin (eg. [0, 10, 20] in
        degrees). Must be of length ``l``.

    Returns
    -------
    df : :class:`pandas.DataFrame`
        Data frame with read in data.
    """
    times_ = cdf.varget(timekey)[...]
    utc_comp = cdflib.cdfepoch.breakdown(times_)
    times = np.asarray([dt.datetime(*x) for x in utc_comp])
    ntimesteps = times.size
    energies = cdf.varget(energykey)[...]
    # If energies is 2D, just take first set of energies
    if len(energies.shape) == 2:
        energies = energies[0, :]

    # Empty lists. index[0] will be times, index[1] will be energies, index[2]
    # will be angles. data will be the pdf
    index = [[], [], []]
    data = []
    # Loop through energies
    for i, key in enumerate(distkeys):
        thisenergy = energies[i]
        this_e_data = cdf.varget(key)[...]
        # Loop through angles
        for j in range(0, this_e_data.shape[1]):
            # Time steps
            index[0] += list(times)
            # Current energy
            index[1] += [thisenergy] * ntimesteps
            # Current angle
            index[2] += [anglelabels[j]] * ntimesteps

            thisdata = this_e_data[:, j]
            thisdata[thisdata == -9.99999985e+30] *= np.nan
            data += list(thisdata)

    tuples = list(zip(*index))
    index = pd.MultiIndex.from_tuples(tuples,
                                      names=['Time', 'Energy', 'Angle'])
    data = pd.DataFrame(data, index=index, columns=['df'])
    data = data.sort_index()
    return data


def cdf2df(cdf, index_key, dtimeindex=True, badvalues=None,
           ignore=None, include=None):
    """
    Converts a cdf file to a pandas dataframe.

    Note that this only works for 1 dimensional data, other data such as
    distribution functions or pitch angles will not work properly.

    Parameters
    ----------
    cdf : cdf
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
            fillval = cdf.varattsget(cdf_key)['FILLVAL']
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


def load(filename, local_dir, remote_url,
         try_download=True, remote_error=False):
    """
    Try to load a file from *local_dir*.

    If file doesn't exist locally, try to download from *remtote_url* instead.

    Parameters
    ----------
    filename : str
        Name of file
    local_dir : str
        Local location of file
    remote_url : str
        Remote location of file
    try_download : bool
        If a file isn't available locally, try to downloaded it. Default is
        *True*.
    remote_error : bool
        If ``True``, raise an error if the requested file isn't present
        locally or remotely. If ``False``, the method returns ``None`` if
        the file can't be found.

    Returns
    -------
    file : CDF, open file, None
        If *filename* ends in *.cdf* the CDF file will be opened and
        returned.

        Otherwise it is assumed that the file is an ascii file, and
        *filename* will be opened using python's :func:`open` method.

        If the file can't be found locally or remotely, and *remote_errror* is
        ``False``, ``None`` is returned.
    """
    # Check if file is cdf
    if filename[-4:] == '.cdf':
        filetype = 'cdf'
    # If not a cdf file assume ascii file
    else:
        filetype = 'ascii'

    # Try to load locally
    if _checkdir(local_dir):
        local_dir = path.Path(local_dir)
        for f in local_dir.iterdir():
            if str(f) == filename or ((str(f)[:-6] == filename[:-6])):
                return _load_local(local_dir / f, filetype)

    if try_download:
        try:
            return _load_remote(remote_url, filename, local_dir, filetype)
        except urlerror.URLError:
            if remote_error:
                raise RemoteFileNotFoundError(
                    'File {}/{} not available'.format(remote_url, filename))
            else:
                return None
    else:
        return None


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


def _download_remote(remote_url, filename, local_dir):
    dl_path = path.Path(local_dir) / filename
    remote_url = _fix_url(remote_url)
    remote_url = remote_url + '/' + filename
    _download_url(remote_url, dl_path)


def _download_url(url, local_path):
    """
    Download *url* to *local_path*.
    """
    logger.info(f'Looking for {url}')
    with requests.head(url) as r:
        if r.status_code != requests.codes.ok:
            raise NoDataError(
                f'{url} returned bad status code {r.status_code}')
    # TODO change this print statement to a logging statement
    print(f'Downloading {url} to {local_path}')
    fname, _ = urlreq.urlretrieve(url,
                                  filename=str(local_path),
                                  reporthook=_reporthook)
    print('\n')


def _load_remote(remote_url, filename, local_dir, filetype):
    local_dir = path.Path(local_dir)
    _download_remote(remote_url, filename, local_dir)
    return _load_local(local_dir / filename, filetype)


def _fix_url(url):
    '''
    Given a url possibly constructued using an os.path.join method,
    replace all backlslashes with forward slashes to make the url valid
    '''
    if url is not None:
        return url.replace('\\', '/')
    else:
        return url


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


def _daysplitinterval(starttime, endtime):
    """
    Splits an interval into a list of dates, start times and end times

    Parameters
    ----------
    starttime : datetime.datetime
        Start date/time of interval
    endtime : datetime.datetime
        End date/time of interval

    Returns
    -------
    intervals : list
        A list of lists. Each item in the sublists consists of the date,
        start time, and end time for the particular date.
    """
    assert starttime < endtime, 'Start datetime must be before end datetime'
    out = []
    starttime_orig = starttime
    while starttime.date() <= endtime.date():
        if starttime.date() == starttime_orig.date():
            stime = starttime.time()
        else:
            stime = dt.time.min
        if starttime.date() == endtime.date():
            etime = endtime.time()
        else:
            etime = dt.time.max

        out.append([starttime.date(), stime, etime])
        starttime += dt.timedelta(days=1)
    return out


def _cart2sph(x, y, z):
    """
    Given cartesian co-ordinates returns shperical co-ordinates.

    Parameters
    ----------
    x : array_like
        x values
    y : array_like
        y values
    z : array_like
        z values

    Returns
    -------
    r : array_like
        r values
    theta : array_like
        Elevation angles defined from the x-y plane towards the z-axis.
        Angles are in the range [-pi/2, pi/2].
    phi : array_like
        Azimuthal angles defined in the x-y plane, clockwise about the
        z-axis, from the x-axis. Angles are in the range [-pi, pi].
    """
    xy = x**2 + y**2
    r = np.sqrt(xy + z**2)
    theta = np.arctan2(z, np.sqrt(xy))
    phi = np.arctan2(y, x)
    return r, theta, phi


def _sph2cart(r, theta, phi):
    """
    Given spherical co-orinates, returns cartesian coordiantes.

    Parameters
    ----------
    r : array_like
        r values
    theta : array_like
        Elevation angles defined from the x-y plane towards the z-axis
    phi : array_like
        Azimuthal angles defined in the x-y plane, clockwise about the
        z-axis, from the x-axis.

    Returns
    -------
    x : array_like
        x values
    y : array_like
        y values
    z : array_like
        z values
    """
    x = r * np.cos(theta) * np.cos(phi)
    y = r * np.cos(theta) * np.sin(phi)
    z = r * np.sin(theta)
    return x, y, z


def doy2ymd(y, doy):
    """
    Converts day of year and year to year, month, day

    Parameters
    ----------
    y : int
        Year
    doy : int
        Day of year

    Returns
    -------
    year : int
        Year
    month : int
        Month
    day : int
        Day of month
    """
    d = dt.datetime.strptime(str(y) + ':' + str(doy), '%Y:%j')

    return d.year, d.month, d.day


def dtime2doy(dt):
    """
    Returns day of year of a datetime object.

    Parameters
    ----------
    dt : datetime.datetime

    Returns
    -------
    doy : int
        Day of year
    """
    return int(dt.strftime('%j'))
