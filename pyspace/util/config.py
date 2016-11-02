'''
Pyspace configuration utility
'''
import configparser
import os
import pyspace


def load_config():
    '''
    Read in configuration file
    '''
    config_filename = 'pyspacerc'

    config = configparser.ConfigParser()
    # Get configuration location
    module_dir = os.path.dirname(pyspace.__file__)
    config_file = os.path.join(module_dir, 'data', config_filename)
    # Read and return configuration
    config.read(config_file)
    return config
