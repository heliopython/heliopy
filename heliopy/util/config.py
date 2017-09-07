"""
heliopy configuration utility
"""
import configparser
import os
import heliopy


def get_config_file():
    """
    Return location of configuration file. This looks in the following places
    in order:

    1. ~/.heliopy/heliopyrc
    2. The installation folder of heliopy

    Returns
    -------
    loc : string
        Filepath of the ``heliopyrc`` configuration file
    """
    config_filename = 'heliopyrc'

    # Get user configuration location
    home_dir = os.path.expanduser("~")
    config_file_1 = os.path.join(home_dir, '.heliopy', config_filename)

    module_dir = os.path.dirname(heliopy.__file__)
    config_file_2 = os.path.join(module_dir, config_filename)

    for f in [config_file_1, config_file_2]:
        if os.path.isfile(f):
            return f


def load_config():
    """
    Read in configuration file. This looks in the following places in order:

    1. ~/.heliopy/heliopyrc
    2. The installation folder of heliopy

    Returns
    -------
    config : dict
        Dictionary containing configuration options read from ``heliopyrc``
    """
    config_location = get_config_dir()
    config = configparser.ConfigParser()
    config.read(config_location)

    # Set data download directory
    download_dir = os.path.expanduser(config['DEFAULT']['download_dir'])
    config['DEFAULT']['download_dir'] = download_dir
    # Create data download if not created
    if not os.path.isdir(download_dir):
        print('Creating download directory {}'.format(download_dir))
        os.makedirs(download_dir)

    # Set cluster cookie
    # Check environment variables for a cluster cookie
    if os.environ.get('CLUSTERCOOKIE') is not None and\
            config['DEFAULT']['cluster_cookie'] == 'none':
        config['DEFAULT']['cluster_cookie'] = os.environ.get('CLUSTERCOOKIE')

    return config
