"""Helper methods for importing data"""
import os
import sys
from spacepy import pycdf
from urllib.request import urlretrieve
import pandas as pd


def _reporthook(blocknum, blocksize, totalsize):
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
        sys.stderr.write("read %d\n" % (readsofar,))


def checkdir(directory):
    """Checks if directory exists, if not creates directory"""
    if not os.path.exists(directory):
        print('Creating new directory', directory)
        os.makedirs(directory)


def load(filename, local_dir, remote_url):
    """
    Try to load a file from local_dir.

    If file doesn't exist locally, try to download from remtote_url instead.
    """
    # Check if file is cdf
    if filename[-4:] == '.cdf':
        filetype = 'cdf'
    # If not a cdf file assume ascii file
    else:
        filetype = 'ascii'

    # If file doesn't exist locally, attempt to download file
    if not os.path.isfile(local_dir + '/' + filename):
        print('Downloading', remote_url + '/' + filename)
        urlretrieve(remote_url + '/' + filename,
                    filename=local_dir + '/' + filename,
                    reporthook=_reporthook)

    # Import local file
    if filetype == 'cdf':
        cdf = pycdf.CDF(local_dir + '/' + filename)
        return cdf
    elif filetype == 'ascii':
        # TODO: Read in ascii files
        print('Ascii importing not working yet')


def cdf2df(cdf, index_key, keys, dtimeindex=True):
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

    Returns
    -------
        df : DataFrame
            Data frame with read in data.
    """
    index = cdf[index_key][...][:, 0]
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
    return df
