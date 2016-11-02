'''
Helper methods for importing data
'''
import os
from spacepy import pycdf
from urllib.request import urlretrieve


def checkdir(directory):
    '''
    Checks if directory exists, if not creates directory
    '''
    if not os.path.exists(directory):
        os.makedirs(directory)


def load(filename, local_dir, remote_url):
    '''
    Try to load a file from local_dir
    If file doesn't exist, try to download from remtote_url
    '''
    # Check if file is cdf
    if filename[-4:] == '.cdf':
        filetype = 'cdf'
    # If not a cdf file assume ascii file
    else:
        filetype = 'ascii'

    # If file doesn't exist locally, attempt to download file
    if not os.path.isfile(local_dir + '/' + filename):
        urlretrieve(remote_url + '/' + filename,
                    filename=local_dir + '/' + filename)

    # Import local file
    if filetype == 'cdf':
        cdf = pycdf.CDF(local_dir + '/' + filename)
        return cdf
    elif filetype == 'ascii':
        # TODO: Read in ascii files
        print('Ascii importing not working yet')
