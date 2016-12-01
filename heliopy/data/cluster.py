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
generic_dict = {'DELIVERY_FORMAT': 'CDF',
                'REF_DOC': '0',
                'CSACOOKIE': cda_cookie,
                'INCLUDE_EMPTY': '0'
                }
# Time string format for cluster data archive.
cda_time_fmt = '%Y-%m-%dT%H:%M:%SZ'


def fgm(probe, starttime, endtime):
    """
    Download fluxgate magnetometer data.

    Parameters
    ----------
        probe : string
            Probe number. Must be '1', '2', '3', or '4'.
        starttime : datetime
            Interval start.
        endtime : datetime
            Interval end.

    Returns
    -------
        data : DataFrame
            Requested data.
    """
    # Add start and end time to request dictionary
    request_dict = generic_dict
    request_dict['START_DATE'] = starttime.strftime(cda_time_fmt)
    request_dict['END_DATE'] = endtime.strftime(cda_time_fmt)

    # Work out dataset ID
    request_str = ''
    request_str += 'DATASET_ID' + '='
    request_str += 'C' + probe + '_CP_FGM_FULL'
    for item in request_dict:
        request_str += '&'
        request_str += item
        request_str += '='
        request_str += request_dict[item]

    url = 'https://csa.esac.esa.int/csa/aio/product-action?'
    request_str += '&NON_BROWSER'

if __name__ == '__main__':
    fgm('2', datetime(2004, 6, 18, 11, 35, 0), datetime(2004, 6, 19, 18, 35, 0))
