"""heliopy configuration utility"""
import configparser
import os
import heliopy


def load_config():
    """Read in configuration file"""
    config_filename = 'heliopyrc'
    config = configparser.ConfigParser()

    # Get user configuration location
    home_dir = os.path.expanduser("~")
    config_file_1 = os.path.join(home_dir, '.heliopy', config_filename)

    module_dir = os.path.dirname(heliopy.__file__)
    config_file_2 = os.path.join(module_dir, config_filename)

    for f in [config_file_1, config_file_2]:
        if os.path.isfile(f):
            print('Reading config')
            config.read(f)
            break
    print(config.sections())
    # Set data download directory
    download_dir = os.path.join(home_dir, config['DEFAULT']['download_dir'])
    config['DEFAULT']['download_dir'] = download_dir
    # Create data download if not created
    if not os.path.isdir(download_dir):
        print('Creating download directory %s' % download_dir)
        os.mkdir(download_dir)

    # Set cluster cookie
    # Check environment variables for a cluster cookie
    if os.environ.get('CLUSTERCOOKIE') is not None and\
            config['DEFAULT']['cluster_cookie'] == 'none':
        config['DEFAULT']['cluster_cookie'] = os.environ.get('CLUSTERCOOKIE')

    return config
