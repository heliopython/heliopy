"""
Methods for importing data from the four Cluster spacecraft.

To download data you will need to be registered at the cluster science archive
(http://www.cosmos.esa.int/web/csa/register-now), and have set either the
environment variable CLUSTERCOOKIE to your cookie, or set your cookie in
the `heliopyrc` file.

The data download method is described at
https://csa.esac.esa.int/csa/aio/html/wget.shtml.
"""
import os
import tarfile
from datetime import datetime, time
import urllib.request as urlreq
import numpy as np

from heliopy import config
from heliopy.data import util

data_dir = config['download_dir']
cda_cookie = config['cluster_cookie']
csa_url = 'https://csa.esac.esa.int/csa/aio/product-action?'
cluster_dir = os.path.join(data_dir, 'cluster')

# Create request dictionary to which the data product, start time and end times
# can be added to later.
generic_dict = {'DELIVERY_FORMAT': 'CDF',
                'REF_DOC': '0',
                'CSACOOKIE': cda_cookie,
                'INCLUDE_EMPTY': '0'
                }
# Time string format for cluster data archive.
cda_time_fmt = '%Y-%m-%dT%H:%M:%SZ'


def _load(probe, starttime, endtime, instrument, product_id, cdfkeys):
    daylist = util._daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        year = str(date.year)
        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        local_dir = os.path.join(cluster_dir,
                                 'c' + probe,
                                 instrument,
                                 year)

        local_fname = 'C' + probe + '_' + product_id + '__' +\
            year + month + day + '.cdf'
        # If we don't have local file download it
        if not os.path.exists(os.path.join(local_dir, local_fname)):
            thisstart = datetime.combine(date, time.min)
            thisend = datetime.combine(date, time.max)
            try:
                _download(probe, thisstart, thisend, instrument, product_id)
            except Exception as err:
                print(str(err), '\n')
                continue

        from pycdf import pycdf
        cdf = pycdf.CDF(os.path.join(local_dir, local_fname))
        for key, value in cdfkeys.items():
            if value == 'Time':
                index_key = key
                break
        data.append(util.cdf2df(cdf, index_key, cdfkeys))
    if len(data) == 0:
        raise RuntimeError('No data available to download during requested '
                           'times')
    return util.timefilter(data, starttime, endtime)


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
        local_dir = os.path.join(cluster_dir,
                                 'c' + probe,
                                 instrument,
                                 year)
        # Work out local filename to download to
        filename = 'C' + probe + '_' + product_id + '__' + year + month +\
            day + '.tar.gz'
        print(request_url)
        # Download data
        util._checkdir(local_dir)
        urlreq.urlretrieve(request_url,
                           filename=os.path.join(local_dir, filename),
                           reporthook=util._reporthook)
        print('\n')
        # Extract tar.gz file
        tar = tarfile.open(os.path.join(local_dir, filename))
        tar.extractall(local_dir)
        # Delete tar.gz file
        os.remove(os.path.join(local_dir, filename))
        # The CSA timpstamps the downloaded file by when it is downloaded,
        # so manually list and retrieve the folder name
        dirlist = os.listdir(local_dir)
        for d in dirlist:
            if d[:13] == 'CSA_Download_':
                download_dir = os.path.join(local_dir,
                                            d,
                                            'C' + probe + '_' + product_id)
                break

        # Remove request times from filename
        dirlist = os.listdir(download_dir)
        # Move to data folder
        cutoff = 3 + len(product_id) + 10
        for f in dirlist:
            os.rename(os.path.join(download_dir, f),
                      os.path.join(local_dir, f[:cutoff] + '.cdf'))
        # Delte extra folders created by tar.gz file
        os.rmdir(download_dir)
        os.rmdir(os.path.join(local_dir, d))


def fgm(probe, starttime, endtime):
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
        data : DataFrame
            Requested data.
    """
    cdfkeys = {'B_mag__C' + probe + '_CP_FGM_FULL': 'Bmag',
               'B_vec_xyz_gse__C' + probe + '_CP_FGM_FULL': ['Bx', 'By', 'Bz'],
               'time_tags__C' + probe + '_CP_FGM_FULL': 'Time'}
    return _load(probe, starttime, endtime, 'fgm', 'CP_FGM_FULL', cdfkeys)


def cis_codif_h1_moms(probe, starttime, endtime, sensitivity='high'):
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
    cdfkeys = {'density__C' + probe + endstr: 'n_h',
               # 'pressure__C' + probe + endstr: 'p_h',
               'T__C' + probe + endstr: 'Th',
               'T_par__C' + probe + endstr: 'Th_par',
               'T_perp__C' + probe + endstr: 'Tg_perp',
               'velocity__C' + probe + endstr: ['vh_x',
                                                'vh_y',
                                                'vh_z'],
               'time_tags__C' + probe + endstr: 'Time'}
    return _load(probe, starttime, endtime, 'peace', endstr[1:], cdfkeys)


def peace_moments(probe, starttime, endtime):
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
    cdfkeys = {'Data_Density__C' + probe + '_CP_PEA_MOMENTS': 'n_e',
               'Data_HeatFlux_GSE__C' + probe + '_CP_PEA_MOMENTS': ['qe_x',
                                                                    'qe_y',
                                                                    'qe_z'],
               'Data_Temperature_ComponentParallelToMagField__C' +
               probe + '_CP_PEA_MOMENTS': 'Te_par',
               'Data_Temperature_ComponentPerpendicularToMagField__C' +
               probe + '_...MOMENTS': 'Te_perp',
               'Data_Velocity_GSE__C' + probe + '_CP_PEA_MOMENTS': ['ve_x',
                                                                    've_y',
                                                                    've_z'],
               'time_tags__C' + probe + '_CP_PEA_MOMENTS': 'Time'}
    return _load(probe, starttime, endtime, 'peace', 'CP_PEA_MOMENTS',
                 cdfkeys)


def cis_hia_onboard_moms(probe, starttime, endtime):
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
    cdfkeys = {'density__C' + probe + '_CP_CIS-HIA_ONBOARD_MOMENTS': 'n_i',
               'pressure__C' + probe + '_CP_CIS-HIA_ONBOARD_MOMENTS': 'p_i',
               'temperature__C' + probe + '_CP_CIS-HIA_ONBOARD_MOMENTS':
               'Ti',
               'temp_par__C' + probe + '_CP_CIS-HIA_ONBOARD_MOMENTS':
               'Ti_par',
               'temp_perp__C' + probe + '_CP_CIS-HIA_ONBOARD_MOMENTS':
               'Ti_perp',
               'velocity_gse__C' + probe + '_CP_CIS-HIA_ONBOARD_MOMENTS':
               ['vi_x',
                'vi_y',
                'vi_z'],
               'time_tags__C' + probe + '_CP_CIS-HIA_ONBOARD_MOMENTS': 'Time'}
    data = _load(probe, starttime, endtime, 'cis',
                 'CP_CIS-HIA_ONBOARD_MOMENTS', cdfkeys)
    to_replace = {'vi_x': -1.803100937500000000e+05}
    data = data.replace(to_replace, np.nan)
    return data
