"""
Methods for importing data from the four Cluster spacecraft.

To download data you will need to be registered at the cluster science archive
(http://www.cosmos.esa.int/web/csa/register-now).

The data download method is described at
https://csa.esac.esa.int/csa/aio/html/wget.shtml.
"""
import os
import tarfile
from heliopy import config
from datetime import datetime, time
from urllib.request import urlretrieve
from heliopy.time import daysplitinterval
from heliopy.data.helper import reporthook, checkdir

data_dir = config['default']['download_dir']
cda_cookie = config['cluster']['user_cookie']
csa_url = 'https://csa.esac.esa.int/csa/aio/product-action?'
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

    https://caa.estec.esa.int/documents/UG/CAA_EST_UG_FGM_v60.pdf

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
    daylist = daysplitinterval(starttime, endtime)
    for day in daylist:
        date = day[0]
        start = datetime.combine(date, time.min)
        end = datetime.combine(date, time.max)
        # Add start and end time to request dictionary
        request_dict = generic_dict
        request_dict['START_DATE'] = start.strftime(cda_time_fmt)
        request_dict['END_DATE'] = end.strftime(cda_time_fmt)

        # Create request string
        request_str = ''
        request_str += 'DATASET_ID' + '='
        request_str += 'C' + probe + '_CP_FGM_FULL'
        for item in request_dict:
            request_str += '&'
            request_str += item
            request_str += '='
            request_str += request_dict[item]

        # Create request url
        request_str += '&NON_BROWSER'
        request_url = csa_url + request_str

        # Work out local directory to download to
        year = str(starttime.year)
        month = str(starttime.month).zfill(2)
        day = str(starttime.day).zfill(2)
        local_dir = cluster_dir + '/c' + probe + '/fgm/full/' + year
        # Work out local filename to download to
        filename = 'C' + probe + '_CP_FGM_FULL__' + year + month + day + '.tar.gz'
        print(request_url)
        # Download data
        checkdir(local_dir)
        urlretrieve(request_url,
                    filename=local_dir + '/' + filename,
                    reporthook=reporthook)
        # Extract tar.gz file
        tar = tarfile.open(local_dir + '/' + filename)
        tar.extractall(local_dir)
        # Delete tar.gz file
        os.remove(local_dir + '/' + filename)
        # The CSA timpstamps the downloaded file by when it is downloaded, so
        # manually list and retrieve the folder name
        dirlist = os.listdir(local_dir)
        for d in dirlist:
            if d[:13] == 'CSA_Download_':
                download_dir = local_dir + '/' + d + '/C2_CP_FGM_FULL'
                break
        print(download_dir)
        # Remove request times from filename
        dirlist = os.listdir(download_dir)
        # Move to data folder
        for f in dirlist:
            os.rename(download_dir + '/' + f, local_dir + '/' + f[:24] + '.cdf')
        # Delte extra folders created by tar.gz file
        os.rmdir(download_dir)
        os.rmdir(local_dir + '/' + d)

if __name__ == '__main__':
    fgm('2', datetime(2004, 6, 18, 11, 35, 0), datetime(2004, 6, 19, 18, 35, 0))
