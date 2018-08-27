"""
Methods for importing data from the four Cluster spacecraft.

To download data you will need to be registered at the cluster science archive
(http://www.cosmos.esa.int/web/csa/register-now), and have set either the
environment variable CLUSTERCOOKIE to your cookie, or set your cookie in
the `heliopyrc` file.

The data download method is described at
https://csa.esac.esa.int/csa/aio/html/wget.shtml.
"""
from datetime import datetime, time

import os
import pathlib as path
import tarfile
import urllib.request as urlreq

import numpy as np

from heliopy import config
from heliopy.data import util

data_dir = path.Path(config['download_dir'])
cda_cookie = config['cluster_cookie']
csa_url = 'https://csa.esac.esa.int/csa/aio/product-action?'
cluster_dir = data_dir / 'cluster'

# Create request dictionary to which the data product, start time and end times
# can be added to later.
generic_dict = {'DELIVERY_FORMAT': 'CDF',
                'REF_DOC': '0',
                'CSACOOKIE': cda_cookie,
                'INCLUDE_EMPTY': '0'
                }
# Time string format for cluster data archive.
cda_time_fmt = '%Y-%m-%dT%H:%M:%SZ'


def _load(probe, starttime, endtime, instrument, product_id,
          try_download):
    dirs = []
    fnames = []
    download_info = []
    for day in util._daysplitinterval(starttime, endtime):
        date = day[0]
        year = str(date.year)
        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        dirs.append(year)
        local_fname = 'C' + probe + '_' + product_id + '__' +\
            year + month + day
        fnames.append(local_fname)
        thisstart = datetime.combine(date, time.min)
        thisend = datetime.combine(date, time.max)
        download_info.append((thisstart, thisend))

    extension = '.cdf'
    local_base_dir = cluster_dir / ('c' + probe) / instrument
    remote_base_url = csa_url

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension,
                      download_info):
        starttime, endtime = download_info
        _download(probe, starttime, endtime, instrument, product_id)

    def processing_func(file):
        for non_empty_var in list(file.cdf_info().keys()):
            if 'variable' in non_empty_var.lower():
                if len(file.cdf_info()[non_empty_var]) > 0:
                    var_list = non_empty_var
                    break

        for key in file.cdf_info()[var_list]:
            if 'CDF_EPOCH' in file.varget(key, expand=True).values():
                index_key = key
                break
        return util.cdf2df(file, index_key)

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, try_download=try_download,
                        units=None,
                        download_info=download_info)


def _download(probe, starttime, endtime, instrument, product_id):
    if cda_cookie == 'none':
        raise RuntimeError('Cluster download cookie not set')
    daylist = util._daysplitinterval(starttime, endtime)
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
        request_str += 'C' + probe + '_' + product_id
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
        local_dir = cluster_dir / ('c' + probe) / instrument / year
        local_fname = 'C' + probe + '_' + product_id + '__' +\
            year + month + day + '.cdf'
        local_file = local_dir / local_fname
        print(request_url)
        # Download data
        util._checkdir(local_dir)
        urlreq.urlretrieve(request_url,
                           filename=local_file,
                           reporthook=util._reporthook)
        print('\n')
        # Extract tar.gz file
        tar = tarfile.open(local_file)
        tar.extractall(local_dir)
        # Delete tar.gz file
        os.remove(local_file)
        # The CSA timpstamps the downloaded file by when it is downloaded,
        # so manually list and retrieve the folder name
        dirlist = os.listdir(local_dir)
        for d in dirlist:
            if d[:13] == 'CSA_Download_':
                download_dir = local_dir / d / ('C' + probe + '_' + product_id)
                break

        # Remove request times from filename
        dirlist = os.listdir(download_dir)
        # Move to data folder
        cutoff = 3 + len(product_id) + 10
        for f in dirlist:
            os.rename(download_dir / f,
                      local_dir / (f[:cutoff] + '.cdf'))
        # Delte extra folders created by tar.gz file
        os.rmdir(download_dir)
        os.rmdir(os.path.join(local_dir, d))


def fgm(probe, starttime, endtime, try_download=True):
    """
    Download fluxgate magnetometer data.

    See https://caa.estec.esa.int/documents/UG/CAA_EST_UG_FGM_v60.pdf for more
    information on the FGM data.

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
        data : :class:`~sunpy.timeseries.TimeSeries`
            Requested data.
    """
    return _load(probe, starttime, endtime, 'fgm', 'CP_FGM_FULL',
                 try_download=try_download)


def cis_codif_h1_moms(probe, starttime, endtime, sensitivity='high',
                      try_download=True):
    """
    Load H+ moments from CIS instrument.

    See https://caa.estec.esa.int/documents/UG/CAA_EST_UG_CIS_v35.pdf for more
    information on the CIS data.

    Parameters
    ----------
    probe : string
        Probe number. Must be '1', '2', '3', or '4'.
    starttime : datetime
        Interval start.
    endtime : datetime
        Interval end.
    sensitivity : string, 'high' or 'low', default: 'low'
        Load high or low sensitivity

    Returns
    -------
    data : DataFrame
        Requested data.
    """
    sensitivitydict = {'high': 'HS', 'low': 'LS'}
    sensitivity = sensitivitydict[sensitivity]
    endstr = '_CP_CIS-CODIF_' + sensitivity + '_H1_MOMENTS'
    return _load(probe, starttime, endtime, 'peace', endstr[1:],
                 try_download=try_download)


def peace_moments(probe, starttime, endtime, try_download=True):
    """
    Download electron moments from the PEACE instrument.

    See https://caa.estec.esa.int/documents/UG/CAA_EST_UG_PEA_v25.pdf for more
    information on the PEACE data.

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
    return _load(probe, starttime, endtime, 'peace', 'CP_PEA_MOMENTS',
                 try_download=try_download)


def cis_hia_onboard_moms(probe, starttime, endtime, try_download=True):
    """
    Download onboard ion moments from the CIS instrument.

    See https://caa.estec.esa.int/documents/UG/CAA_EST_UG_CIS_v35.pdf for more
    information on the CIS data.

    Parameters
    ----------
        probe : string
            Probe number. Must be '1' or '3'
        starttime : datetime
            Interval start.
        endtime : datetime
            Interval end.

    Returns
    -------
        data : DataFrame
            Requested data.
    """
    if probe == '2' or probe == '4':
        raise ValueError('Onboard ion moment data is not available for '
                         'cluster probes 2 or 4')
    data = _load(probe, starttime, endtime, 'cis',
                 'CP_CIS-HIA_ONBOARD_MOMENTS',
                 try_download=try_download)
    return data
