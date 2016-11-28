"""
Methods for importing data from the four Cluster spacecraft.

To download data you will need to be registered at the cluster science archive
(http://www.cosmos.esa.int/web/csa/register-now).

The data download method is described at
https://csa.esac.esa.int/csa/aio/html/wget.shtml.
"""
from heliopy import config
from datetime import datetime

data_dir = config['default']['download_dir']
cda_cookie = config['cluster']['user_cookie']
cluster_dir = data_dir + '/cluster'
# Create request dictionary to which the data product, start time and end times
# can be added to later.
generic_dict = {'RETRIEVALTYPE': 'PRODUCT',
                'DELIVERY_FORMAT': 'CDF',
                'DELIVERY_INTERVAL': 'daily',
                'REF_DOC': '0',
                'NON_BROWSER': '',
                'CSACOOKIE': cda_cookie,
                'INCLUDE_EMPTY': '0'
                }
# Time string format for cluster data archive.
cda_time_fmt = '%Y-%m-%dT%H:%M:%SZ'


def fgm(starttime, endtime):
    # Add start and end time to request dictionary
    request_dict = generic_dict
    request_dict['START_DATE'] = starttime.strftime(cda_time_fmt)
    request_dict['START_DATE'] = endtime.strftime(cda_time_fmt)

    request_str = ''
    for item in request_dict:
        request_str += '?'
        request_str += item
        request_str += '='
        request_str += request_dict[item]

if __name__ == '__main__':
    fgm(datetime(2001, 1, 1, 0, 0, 0), datetime(2001, 1, 2, 0, 0, 0))
