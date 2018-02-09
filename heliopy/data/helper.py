"""Helper methods for importing data"""
import os
import sys
from urllib.error import URLError
import urllib.request as urlreq
import ftplib
from datetime import datetime, time, timedelta

import pandas as pd
import numpy as np

from heliopy import config

__all__ = ['cdfpeek', 'listdata', 'timefilter', 'load', 'cdf2df']


def _bytes2str(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in [' B', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.2f %s" % (num, x)
        num /= 1024.0


def cdfpeek(cdf_loc):
    """
    List all the variables present in a CDF file, along with their size.

    Parameters
    ----------
    cdf_loc : string
        Local location of the cdf file.
    """
    from pycdf import pycdf
    cdf = pycdf.CDF(cdf_loc)
    print(cdf)


def listdata(probes=None):
    """
    Print amount of data stored locally in the heliopy data directory.

    Prints a table to the terminal with a column for raw data and a column
    for converted hdf data files.

    Example output ::

        Scanning files in /Users/dstansby/Data/
        ----------------------------------------
        |      Probe |        Raw |        HDF |
        |--------------------------------------|
        |        ace |    1.44 MB |  800.00  B |
        |    cluster |  200.39 MB |    0.00  B |
        |     helios |    2.37 GB |    1.41 GB |
        |        imp |   19.76 MB |   28.56 MB |
        |  messenger |   15.24 MB |   27.21 MB |
        |        mms |   70.11 MB |    0.00  B |
        |     themis |   64.31 MB |    0.00  B |
        |    ulysses |   54.78 MB |   47.98 MB |
        |       wind |  176.84 MB |   63.82 MB |
        |--------------------------------------|
        |--------------------------------------|
        |      Total |    2.96 GB |    1.57 GB |
        ----------------------------------------

    Parameters
    ----------
    probes : List of strings, optional
        Probe names

    """
    data_dir = config['download_dir']
    if probes is None:
        probes = os.listdir(data_dir)

    # Remove directories that start with a .
    probes = [probe for probe in probes if probe[0] != '.']
    probes = sorted(probes)

    sizes = np.zeros((len(probes), 2))
    for i, probe in enumerate(probes):
        probe_dir = os.path.join(data_dir, probe)
        for dirname, dirnames, filenames in os.walk(probe_dir):
            for f in filenames:
                fsize = os.stat(os.path.join(dirname, f)).st_size
                if f.endswith('.hdf'):
                    sizes[i, 1] += fsize
                else:
                    sizes[i, 0] += fsize

    probes.append('Total')
    sizes = np.row_stack((sizes, np.sum(sizes, axis=0)))

    original_sizes = [_bytes2str(size) for size in sizes[:, 0]]
    hdf_sizes = [_bytes2str(size) for size in sizes[:, 1]]

    probes = ['Probe'] + probes
    original_sizes = ['Raw'] + original_sizes
    hdf_sizes = ['HDF'] + hdf_sizes

    def pad(lst):
        maxlen = max([len(item) for item in lst])
        lst = [''.ljust(maxlen - len(item) + 1) + item for item in lst]
        return lst, maxlen

    probes, probelen = pad(probes)
    original_sizes, origlen = pad(original_sizes)
    hdf_sizes, hdflen = pad(hdf_sizes)

    total_len = probelen + origlen + hdflen + 13

    rowfmt = '| {} | {} | {} |'
    divider = '|' + '-' * (total_len - 2) + '|'
    # Do actual printing
    print('Scanning files in {}'.format(data_dir))
    # Header column
    print('-' * total_len)
    # Each probe in turn
    for i, (probe, original_size, hdf_size) in enumerate(
            zip(probes, original_sizes, hdf_sizes)):
        # Add two dividers before total
        if i == len(probes) - 1:
            print(divider)
            print(divider)

        # Print each row
        print(rowfmt.format(probe, original_size, hdf_size))

        # Add one divider after header
        if i == 0:
            print(divider)
    print('-' * total_len)


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
            stime = time.min
        if starttime.date() == endtime.date():
            etime = endtime.time()
        else:
            etime = time.max

        out.append([starttime.date(), stime, etime])
        starttime += timedelta(days=1)
    return out


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
    d = datetime.strptime(str(y) + ':' + str(doy), '%Y:%j')

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


def _load_local(local_dir, filename, filetype):
    # Import local file
    if filetype == 'cdf':
        from pycdf import pycdf
        cdf = pycdf.CDF(os.path.join(local_dir, filename))
        return cdf
    elif filetype == 'ascii':
        f = open(os.path.join(local_dir, filename))
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


def _load_remote(remote_url, filename, local_dir, filetype):
    print('Downloading', remote_url + '/' + filename)
    urlreq.urlretrieve(remote_url + '/' + filename,
                       filename=os.path.join(local_dir, filename),
                       reporthook=_reporthook)
    print('\n')
    return _load_local(local_dir, filename, filetype)


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
    if not os.path.exists(directory):
        print('Creating new directory', directory)
        os.makedirs(directory)
        return False
    else:
        return True


class RemoteFileNotPresentError(RuntimeError):
    pass


def load(filename, local_dir, remote_url, guessversion=False,
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
    guessversion : bool
        If *True*, try to guess the version number in the filename. Only
        works for cdf files. Default is *False*.
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
        if guessversion:
            raise RuntimeError('Cannot guess version for ascii files')

    # Try to load locally
    if _checkdir(local_dir):
        for f in os.listdir(local_dir):
            if f == filename or guessversion and (f[:-6] == filename[:-6]):
                filename = f
                return _load_local(local_dir, f, filetype)

    # Loading locally failed, but directory has been made so try to download
    # file.
    remote_url = _fix_url(remote_url)
    if guessversion:
        # Split remote url into a server name and directory
        for i, c in enumerate(remote_url[6:]):
            if c == '/':
                server = remote_url[6:6 + i]
                server_dir = remote_url[7 + i:]
                break
        # Login to remote server
        ftp = ftplib.FTP(server)
        ftp.login()
        # List files in directory
        files = ftp.nlst(server_dir)
        ftp.quit()
        # Loop through and find files
        for f in files:
            if f[-len(filename):-8] == filename[:-8]:
                filename = f[-len(filename):]

    if try_download:
        try:
            return _load_remote(remote_url, filename, local_dir, filetype)
        except URLError:
            if remote_error:
                raise RemoteFileNotFoundError(
                    'File {}/{} not available'.format(remote_url, filename))
            else:
                return None
    else:
        return None


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
    times = cdf[timekey][...]
    ntimesteps = times.size
    energies = cdf[energykey][...]
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
        this_e_data = cdf[key][...]
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


def cdf2df(cdf, index_key, keys=None, dtimeindex=True, badvalues=None):
    """
    Converts a cdf file to a pandas dataframe.

    Parameters
    ----------
    cdf : cdf
        Opened cdf file
    index_key : string
        The key to use as indexing in the output dataframe
    keys : dict, optional
        A dictionary that maps keys in the cdf file to the corresponding
        desired keys in the ouput dataframe. If a particular cdf key has
        multiple columns, the mapped keys must be in a list.
    dtimeindex : bool, optional
        If ``True``, DataFrame index is parsed as a datetime.
        Default is ``True``.
    badvalues : dict, optional
        A dictionary that maps the new DataFrame keys to a list of bad
        values to replace with nans.

    Returns
    -------
    df : :class:`pandas.DataFrame`
        Data frame with read in data
    """
    # Extract index values
    try:
        index = cdf[index_key][...][:, 0]
    except IndexError:
        index = cdf[index_key][...]
    # Parse datetime index
    if dtimeindex:
        index = pd.DatetimeIndex(index)
    df = pd.DataFrame(index=index)

    if keys is None:
        keys = {}
        for key in cdf.keys():
            if key == 'Epoch':
                keys['Epoch'] = 'Time'
            else:
                keys[key] = key

    for key in keys:
        df_key = keys[key]
        if isinstance(df_key, list):
            for i, subkey in enumerate(df_key):
                df[subkey] = cdf[key][...][:, i]
        else:
            df[df_key] = cdf[key][...]
    # Replace bad values with nans
    if badvalues is not None:
        df = df.replace(badvalues, np.nan)
    return df
