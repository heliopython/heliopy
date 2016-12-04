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
    config_file = os.path.join(home_dir, '.heliopy', config_filename)
    if os.path.isfile(config_file):
        config.read(config_file)
        return config

    # Get default configuration location
    module_dir = os.path.dirname(heliopy.__file__)
    config_file = os.path.join(module_dir, 'data', config_filename)
    config.read(config_file)
    config['default']['download_dir'] = os.path.join(home_dir,
                                                     config['default']['download_dir'])
    if os.environ.get('CLUSTERCOOKIE') is not None and\
            config['default']['download_dir'] == 'none':
        config['cluster']['user_cookie'] = os.environ.get('CLUSTERCOOKIE')
    return config
