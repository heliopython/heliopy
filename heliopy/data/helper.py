"""
Helper methods for importing data
"""
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
    """
    Checks if directory exists, if not creates directory
    """
    if not os.path.exists(directory):
        print('Creating new directory', directory)
        os.makedirs(directory)


def load(filename, local_dir, remote_url):
    """
    Try to load a file from local_dir
    If file doesn't exist, try to download from remtote_url
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


def cdf2df(cdf):
    """
    Converts a cdf file to a pandas dataframe

    If data in CDF file is n x 3 dimensional, assume it is vector data and
    assign subscripts _x, _y, _z

    Otherwise, if data is n x m where m isn't 1 or 3, skip completely
    """
    df = pd.DataFrame(data={'Time': cdf['Epoch'][...]},
                      index=cdf['Epoch'][...])
    components = ['x', 'y', 'z']
    for key in cdf.keys():
        if key == 'Epoch':
            continue
        # If we only have 1D data
        if len(cdf[key].shape) == 1:
            df[key] = cdf[key][...]
        # If we have more than 1D of data
        if len(cdf[key].shape) == 2:
            # If we have a vector
            if cdf[key].shape[1] == 3:
                for i in range(0, 3):
                    df[key + '_' + components[i]] = cdf[key][...][:, i]
            else:
                continue
    return df
