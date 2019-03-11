"""
Utility functions for data downloading.

**Note**: these methods are liable to change at any time.
"""
import datetime as dt
import ftplib
import io
import logging
import pathlib as path
import re
import shutil
import sys
import urllib.error as urlerror
import urllib.request as urlreq
import astropy.units as u
import sunpy.timeseries as ts
import warnings
import collections as coll
import cdflib

import numpy as np
import pandas as pd
import heliopy.data.helper as helper

from heliopy import config
use_hdf = config['use_hdf']
logger = logging.getLogger(__name__)


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
    fnames : list or str or regex
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
    try_download : bool, optional
        If ``True``, try to download data. If ``False`` don't.
        Default is ``True``.

    units : ~collections.OrderedDict, optional
        Manually defined units to be attached to the data that will be
        returned.

        Must map column headers (strings) to :class:`~astropy.units.Quantity`
        objects. If units are present, then a TimeSeries object is returned,
        else a Pandas DataFrame.

    processing_kwargs : dict, optional
        Extra keyword arguments to be passed to the processing funciton.

    download_info : list, optional
        A list with the same length as *fnames*, which contains extra info
        that is handed to *download_func* for each file individually.
    remote_fnames : list of str, optional
        If the remote filenames are different from the desired downloaded
        filenames, this should be a list of length ``len(fnames)`` with the
        files to be downloaded. The ordering must be the same as *fnames*.
    warn_missing_units : bool, optional
        If ``True``, warnings will be shown for each variable that does not
        have associated units.

    Returns
    -------
    :class:`~pandas.DataFrame` or :class:`~sunpy.timeseries.TimeSeries`
        Requested data.
    """
    local_base_dir = path.Path(local_base_dir)
    data = []
    if download_info == []:
        download_info = [None] * len(dirs)
    if remote_fnames is None:
        remote_fnames = fnames.copy()

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
    out : :class:`~sunpy.timeseries.TimeSeries`
        DataFrame converted into TimeSeries with units attached.
    """
    missing_msg = ('If you are trying to auomatically download data '
                   'with HelioPy this is a bug, please report it at '
                   'https://github.com/heliopython/heliopy/issues')
    unit_key = list(units.keys())
    for column_name in data.columns:
        if column_name not in unit_key:
            units[column_name] = u.dimensionless_unscaled
            if warn_missing_units:
                message = (f"{column_name} column has missing units."
                           f"\n{missing_msg}")
                warnings.warn(message, Warning)
    with warnings.catch_warnings():
        warnings.simplefilter(
            'ignore', 'Discarding nonzero nanoseconds in conversion')
        timeseries_data = ts.TimeSeries(data, units)
    return timeseries_data


def cdf_units(cdf_, manual_units=None, length=None):
    """
    Takes the CDF File and the required keys, and finds the units of the
    selected keys.

    Parameters
    ----------
    cdf_ : cdf
        Opened cdf file
    manual_units : ~collections.OrderedDict, optional
        Manually defined units to be attached to the data that will be
        returned.

    Returns
    -------
    out : :class:`collections.OrderedDict`
        Returns an OrderedDict with units of the selected keys.
    """
    units = coll.OrderedDict()
    key_dict = {}
    var_list = []
    if manual_units is None:
        manual_units = {'NOTEXIST': u.dimensionless_unscaled}
    # To figure out whether rVariable or zVariable needs to be taken
    for attr in list(cdf_.cdf_info().keys()):
        if 'variable' in attr.lower():
            if len(cdf_.cdf_info()[attr]) > 0:
                var_list += [attr]

    # Extract the list of valid keys in the zVar or rVar
    for attr in var_list:
        for key in cdf_.cdf_info()[attr]:
            try:
                y = cdf_.varget(key)
                ncols = y.shape
                if len(ncols) == 1:
                    key_dict[key] = key
                if len(ncols) > 1:
                    val = []
                    val.append(key)
                    for x in range(0, ncols[1]):
                        field = key + "{}".format('_' + str(x))
                        val.append(field)
                    key_dict[key] = val
            except Exception as e:
                print("{}-Variable{}".format(e, key))
                continue

    # Assigning units to the keys
    for key, val in key_dict.items():
        unit_str = None
        temp_unit = None
        try:
            unit_str = cdf_.varattsget(key)['UNITS']
        except KeyError:
            if key in manual_units:
                temp_unit = manual_units[key]
            else:
                continue

        if temp_unit is None:
            try:
                temp_unit = u.Unit(unit_str)
            except (TypeError, ValueError):
                if key in manual_units:
                    temp_unit = manual_units[key]
                elif helper.cdf_dict(unit_str):
                    temp_unit = helper.cdf_dict(unit_str)
                if unit_str is None:
                    message = "The CDF provided units ({}) for key '{}' \
                    are unknown".format(unit_str, key)
                    warnings.warn(message, Warning)
                    continue
        if temp_unit is not None:
            if isinstance(val, list):
                units.update(coll.OrderedDict.fromkeys(val, temp_unit))
            else:
                units[val] = temp_unit
    units.update(manual_units)
    return units


def timefilter(data, starttime, endtime):
    """
    Puts data in a single dataframe, and filters it between times.

    Parameters
    ----------
    data : :class:`pandas.DataFrame` or list
        Input data. If a list, ``pd.concat(data)`` will be run to put it in
        a DataFrame.
    starttime : datetime
        Start of interval.
    endtime : datetime
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
    cdf : cdf
        Opened cdf file.
    distkeys : list
        A list of the cdf keys for a given energies. Each array accessed by
        distkeys is shape `(n, l)`, and there must be `m` distkeys.
    energykey : string
        The cdf key for the energy values. The array accessed by energykey
        must have shape `(m)` or `(a, m)` where `a` can be anything. If it
        has shape `(a, m)`, we assume energies measured don't change, and
        take the first row as the energies for all times.
    timekey : string
        The cdf key for the timestamps. The array access by timekey must
        have shape `(n)`
    anglelabels : list
        A list of the labels to give each anglular bin (eg. [0, 10, 20] in
        degrees). Must be of length `l`.

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


def cdf2df(cdf, index_key, dtimeindex=True, badvalues=None, ignore=None):
    """
    Converts a cdf file to a pandas dataframe.

    Note that this only works for 1 dimensional data, other data such as
    distribution functions or pitch angles will not work properly.

    Parameters
    ----------
    cdf : cdf
        Opened CDF file.
    index_key : string
        The CDF key to use as the index in the output DataFrame.
    dtimeindex : bool, optional
        If ``True``, the DataFrame index is parsed as a datetime.
        Default is ``True``.
    badvalues : dict, list, optional
        A dictionary that maps the new DataFrame column keys to a list of bad
        values to replace with nans. Alternatively a list of numbers which are
        replaced with nans in all columns.
    ignore : list, optional
        In case a CDF file has columns that are unused / not required, then
        the column names can be passed as a list into the function.

    Returns
    -------
    df : :class:`pandas.DataFrame`
        Data frame with read in data.
    """
    # Extract index values
    try:
        index_ = cdf.varget(index_key)[...][:, 0]
    except IndexError:
        index_ = cdf.varget(index_key)[...]
    try:
        utc_comp = cdflib.cdfepoch.breakdown(index_, to_np=True)
        if utc_comp.shape[1] == 9:
            millis = utc_comp[:, 6]*(10**3)
            micros = utc_comp[:, 8]*(10**2)
            nanos = utc_comp[:, 7]
            utc_comp[:, 6] = millis + micros + nanos
            utc_comp = np.delete(utc_comp, np.s_[-2:], axis=1)
        try:
            index = np.asarray([dt.datetime(*x) for x in utc_comp])
        except ValueError:
            utc_comp[:, 6] -= micros
            index = np.asarray([dt.datetime(*x) for x in utc_comp])
    except Exception:
        index = index_
    if dtimeindex:
        index = pd.DatetimeIndex(index, name='Time')
    df = pd.DataFrame(index=index)
    npoints = cdf.varget(index_key).shape[0]

    var_list = []
    for attr in list(cdf.cdf_info().keys()):
        if 'variable' in attr.lower():
            if len(cdf.cdf_info()[attr]) > 0:
                var_list += [attr]

    keys = {}
    for attr in var_list:
        for cdf_key in cdf.cdf_info()[attr]:
            if ignore:
                if cdf_key in ignore:
                    continue
            if cdf_key == 'Epoch':
                keys[cdf_key] = 'Time'
            else:
                keys[cdf_key] = cdf_key
    # Remove index key, as we have already used it to create the index
    keys.pop(index_key)
    # Remove keys for data that doesn't have the right shape to load in CDF
    for cdf_key in keys.copy():
        if type(cdf.varget(cdf_key)) is np.ndarray:
            key_shape = cdf.varget(cdf_key).shape
            if len(key_shape) == 0 or key_shape[0] != npoints:
                keys.pop(cdf_key)
        else:
            keys.pop(cdf_key)

    # Loop through each key and put data into the dataframe
    for cdf_key in keys:
        df_key = keys[cdf_key]
        if isinstance(df_key, list):
            for i, subkey in enumerate(df_key):
                df[subkey] = cdf.varget(cdf_key)[...][:, i]
        else:
            # If ndims is 1, we just have a single column of data
            # If ndims is 2, have multiple columns of data under same key
            key_shape = cdf.varget(cdf_key).shape
            ndims = len(key_shape)
            if ndims == 1:
                df[df_key] = cdf.varget(cdf_key)[...]
            elif ndims == 2:
                for i in range(key_shape[1]):
                    df[df_key + '_' + str(i)] = cdf.varget(cdf_key)[...][:, i]

    # Replace bad values with nans
    if badvalues is not None:
        df = df.replace(badvalues, np.nan)
    return df


class RemoteFileNotPresentError(RuntimeError):
    pass


def load(filename, local_dir, remote_url,
         try_download=True, remote_error=False):
    """
    Try to load a file from *local_dir*.

    If file doesn't exist locally, try to download from *remtote_url* instead.

    Parameters
    ----------
    filename : string
        Name of file
    local_dir : string
        Local location of file
    remote_url : string
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
                filename = str(f)
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


def _get_remote_fname(remote_url, fname_regex):
    '''
    Return a remote filename that matches a regular expression.

    Parameters
    ----------
    remote_url : str
        FTP directory
    fname_regex : str
        Must include extension.

    Retruns
    -------
    fname : str
        Filename that matches including extension.
    '''
    remote_url = _fix_url(remote_url)
    # Split remote url into a server name and directory
    # Strip ftp:// from front of url
    remote_ftp = remote_url[6:]
    for i, c in enumerate(remote_ftp):
        if c == '/':
            server = remote_ftp[:i]
            server_dir = remote_ftp[i:]
            break
    # Login to remote server
    with ftplib.FTP(server) as ftp:
        ftp.login()
        ftp.cwd(server_dir)
        # Loop through and find files
        for (f, _) in ftp.mlsd():
            if re.match(fname_regex, f):
                return f


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


def _download_remote_unknown_version(
    remote_base_url, local_base_dir, directory,
        fname, remote_fname, extension):
    """
    Generic donwload code that can be used by data methods to download
    data where the version is unknown and specified in regex.
    """
    remote_url_dir = remote_base_url + str(directory)
    fname = _get_remote_fname(remote_url_dir, fname)
    local_dir = local_base_dir / directory
    _download_remote(remote_url_dir, fname, local_dir)


def _download_remote(remote_url, filename, local_dir):
    local_dir = path.Path(local_dir)
    remote_url = _fix_url(remote_url)
    remote_url = remote_url + '/' + filename
    print('Downloading', remote_url)
    urlreq.urlretrieve(remote_url,
                       filename=str(local_dir / filename),
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
    directory : string
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
    starttime : datetime
        Start date/time of interval
    endtime : datetime
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
    dt : datetime

    Returns
    -------
    doy : int
        Day of year
    """
    return int(dt.strftime('%j'))
