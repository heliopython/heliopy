"""Helper methods for importing data"""
import os
import sys
from spacepy import pycdf
from urllib.request import urlretrieve
import ftplib
import pandas as pd
import numpy as np


def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        # Near the end
        if readsofar >= totalsize:
            sys.stderr.write("\n")
    # Total size is unknown
    else:
        sys.stderr.write("\rRead %d" % (readsofar,))


def checkdir(directory):
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


def _load_local(local_dir, filename, filetype):
    # Import local file
    if filetype == 'cdf':
        cdf = pycdf.CDF(os.path.join(local_dir, filename))
        return cdf
    elif filetype == 'ascii':
        f = open(os.path.join(local_dir, filename))
        return f


def _load_remote(remote_url, filename, local_dir, filetype):
        print('Downloading', os.path.join(remote_url, filename))
        urlretrieve(remote_url + '/' + filename,
                    filename=os.path.join(local_dir, filename),
                    reporthook=reporthook)
        return _load_local(local_dir, filename, filetype)


def load(filename, local_dir, remote_url, guessversion=False):
    """
    Try to load a file from local_dir.

    If file doesn't exist locally, try to download from remtote_url instead.

    Parameters
    ----------
        filename : string
            Name of file.
        local_dir : string
            Local location of file.
        remote_url : string
            Remote location of file.
        guessversion : bool
            If true, try to guess the version number in the filename. Only works
            for cdf files.
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
    if checkdir(local_dir):
        for f in os.listdir(local_dir):
            if f[:-6] == filename[:-6]:
                filename = f
                return _load_local(local_dir, f, filetype)

    # Loading locally failed, but directory has been made so try to download
    # file.
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
        # Loop through and find files
        for f in files:
            if f[-len(filename):-8] == filename[:-8]:
                filename = f[-len(filename):]

    return _load_remote(remote_url, filename, local_dir, filetype)


def pitchdist_cdf2df(cdf, distkeys, energykey, timekey, anglelabels):
    """
    Converts cdf file of a pitch angle distribution to a pandas dataframe.

    MultiIndexing is used as a pitch angle distribution is essentially a 3D
    dataset f(time, energy, angle). See
    http://pandas.pydata.org/pandas-docs/stable/advanced.html#multiindex-advanced-indexing
    for more information.

    This has been constructed for importing wind swe pitch angle distributions,
    and might not generalise very well to other data sets.

    Assumes that each energy in the cdf has its own 2D array (time, angle). In
    the below description of the function there are
        - `n` time data points
        - `m` energy data points
        - `l` anglular data points

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
        df : DataFrame
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
    index = pd.MultiIndex.from_tuples(tuples, names=['Time', 'Energy', 'Angle'])
    data = pd.Series(data, index=index)
    data = data.sort_index()
    return data


def cdf2df(cdf, index_key, keys, dtimeindex=True, badvalues=None):
    """
    Converts a cdf file to a pandas dataframe.

    Parameters
    ----------
        cdf : cdf
            Opened cdf file.
        index_key : string
            The key to use as indexing in the output dataframe.
        keys : dictionary
            A dictionary that maps keys in the cdf file to the corresponding
            desired keys in the ouput dataframe. If a particular cdf key has
            multiple columns, the mapped keys must be in a list.
        dtimeindex : bool
            If True, dataframe index is parsed as a datetime.
        badvalues : dictionary
            A dictionary that maps the new DataFrame keys to a list of bad
            values to replace with nans.

    Returns
    -------
        df : DataFrame
            Data frame with read in data.
    """
    try:
        index = cdf[index_key][...][:, 0]
    except IndexError:
        index = cdf[index_key][...]
    if dtimeindex:
        index = pd.DatetimeIndex(index)
    df = pd.DataFrame(index=index)

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
