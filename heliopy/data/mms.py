"""
Methods for importing data from the four MMS spacecraft.

All data is publically available at
https://lasp.colorado.edu/mms/sdc/public/data/, and the MMS science data centre
is at https://lasp.colorado.edu/mms/sdc/public/.
"""
from datetime import datetime
import numpy as np
import pandas as pd
import pathlib
from collections import OrderedDict
import astropy.units as u
import requests
import wget

from heliopy.data import util
from heliopy import config

data_dir = pathlib.Path(config['download_dir'])
mms_dir = data_dir / 'mms'
mms_url = 'https://lasp.colorado.edu/mms/sdc/public'
remote_mms_dir = mms_url + '/data/'
query_url = mms_url + '/files/api/v1/file_names/science'
dl_url = mms_url + '/files/api/v1/download/science'


def _validate_instrument(instrument):
    allowed_instruments = ['afg', 'aspoc', 'dfg', 'dsp', 'edi',
                           'edp', 'fpi', 'fields', 'scm', 'sdp', ]
    if instrument not in allowed_instruments:
        raise ValueError(
            'Instrument {} not in list of allowed instruments: {}'.format(
                instrument, allowed_instruments))


def _validate_probe(probe):
    allowed_probes = [str(i) for i in range(4)]
    probe = str(probe)
    if probe not in allowed_probes:
        raise ValueError(
            'Probe {} not in list of allowed probes: {}'.format(
                probe, allowed_probes))
    return probe


def _validate_data_rate(data_rate):
    allowed_rates = ['slow', 'fast', 'brst', 'srvy', '']
    if data_rate not in allowed_rates:
        raise ValueError(
            'Data rate {} not in list of allowed data rates: {}'.format(
                data_rate, allowed_rates))


def available_files(probe, instrument, starttime, endtime, data_rate=''):
    """
    Get available MMS files as a list.

    See the "Query paramters" section of
    https://lasp.colorado.edu/mms/sdc/public/about/how-to/ for more information
    on the query paramters.

    Parameters
    ----------
    probe : int or str
        MMS probe number. Must be in 1-4 inclusive.
    instrument : str
        MMS instrument. Must be in ``['afg', 'aspoc', 'dfg', 'dsp', 'edi',
        'edp', 'fields', 'scm', 'sdp']``
    starttime : datetime
        Start time.
    endtime : datetime
        End time.
    data_rate : str, optional
        Data rate. Must be in ``['slow', 'fast', 'brst', 'srvy']``

    Returns
    -------
    list
        List of file names.
    """
    _validate_instrument(instrument)
    probe = _validate_probe(probe)
    _validate_data_rate(data_rate)
    start_date = starttime.strftime('%Y-%m-%d')
    end_date = endtime.strftime('%Y-%m-%d')

    query = {}
    query['sc_id'] = 'mms' + probe
    query['instrument_id'] = instrument
    if len(data_rate):
        query['data_rate_mode'] = data_rate
    query['start_date'] = start_date
    query['end_date'] = end_date

    r = requests.get(query_url, params=query)
    files = r.text.split(',')
    return files


def download_files(probe, instrument, data_rate, starttime, endtime,
                   verbose=True, product_string=''):
    """
    Get available MMS files as a list.

    See the "Query paramters" section of
    https://lasp.colorado.edu/mms/sdc/public/about/how-to/ for more information
    on the query paramters.

    Parameters
    ----------
    probe : int or str
        MMS probe number. Must be in 1-4 inclusive.
    instrument : str
        MMS instrument. Must be in ``['afg', 'aspoc', 'dfg', 'dsp', 'edi',
        'edp', 'fields', 'scm', 'sdp']``
    data_rate : str
        Data rate. Must be in ``['slow', 'fast', 'brst', 'srvy']``
    starttime : datetime
        Start time.
    endtime : datetime
        End time.
    verbose : bool, optional
        If ``True``, show a progress bar while downloading.
    product_string : str, optional
        If not empty, this string has to be in the filename for it to be
        downloaded.

    Returns
    -------
    df : TimeSeries
        Requested data.
    """
    _validate_instrument(instrument)
    probe = _validate_probe(probe)

    dirs = []
    fnames = []
    daylist = util._daysplitinterval(starttime, endtime)
    for date, stime, etime in daylist:
        files = available_files(probe, instrument,
                                starttime, endtime, data_rate)
        # TODO: make files a proper list
        dirs.append('')
        for file in files:
            fname = pathlib.Path(file).stem
            if product_string in fname:
                fnames.append(fname)

    extension = '.cdf'
    local_base_dir = mms_dir / probe / instrument / data_rate
    remote_base_url = dl_url

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
            url = remote_base_url + '?file=' + fname + extension
            wget.download(url, str(local_base_dir),
                          bar=wget.bar_adaptive if verbose else None)

    def processing_func(cdf):
        return util.cdf2df(cdf, index_key='Epoch')

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime)


def fpi_dis_moms(probe, mode, starttime, endtime):
    """
    Import fpi ion distribution moment data.

    Parameters
    ----------
    probe : string
        Probe number, must be 1, 2, 3, or 4
    mode : string
        Data mode, must be 'fast' or 'brst'
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Imported data.
    """
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='dis-moms')


def fpi_des_moms(probe, mode, starttime, endtime):
    """
    Import fpi electron distribution moment data.

    Parameters
    ----------
    probe : string
        Probe number, must be 1, 2, 3, or 4
    mode : string
        Data mode, must be 'fast' or 'brst'
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Imported data.
    """
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='des-moms')


def fgm_survey(probe, starttime, endtime):
    """
    Import fgm survey mode magnetic field data.

    Parameters
    ----------
    probe : string
        Probe number, must be 1, 2, 3, or 4
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Imported data.
    """

    # Directory relative to main MMS data directory
    relative_dir = pathlib.Path('mms' + probe) / 'fgm' / 'srvy' / 'l2'
    daylist = util._daysplitinterval(starttime, endtime)
    dirs = []
    fnames = []
    # don't need so much string munging since we're asking SDC for things
    extension = '.cdf'
    units = OrderedDict([('mms{}_fgm_mode_srvy_l2'.format(probe),
                          u.dimensionless_unscaled)])

    data = []
    for day in daylist:
        date = day[0]
        this_relative_dir = (relative_dir /
                             str(date.year) /
                             str(date.month).zfill(2))

        # Don't try to request specific versions like this - use the
        # API to grab the most recent file.  The SDC weeps when you
        # expect it to hold old file versions past their prime
        datestring = '{}-{:02}-{:02}'.format(date.year, date.month, date.day)
        datacenter = 'https://lasp.colorado.edu/mms/sdc/public'
        query_base = '/files/api/v1/file_info/science?'
        sdc_req_url = datacenter + query_base
        sdc_date_opts = 'start_date='+datestring+'&end_date='+datestring
        sdc_inst_opts = '&sc_id=mms'+probe+'&instrument_id=fgm'
        sdc_data_opts = '&data_rate_mode=srvy&data_level=l2'
        sdc_opts = sdc_date_opts + sdc_inst_opts + sdc_data_opts
        sdc_fgm_srvy = requests.get(sdc_req_url + sdc_opts)
        filename = sdc_fgm_srvy.json()['files'][0]['file_name']

        filename = filename[:-4]

        fnames.append(filename)
        dirs.append(this_relative_dir)

    remote_base_url = remote_mms_dir
    local_base_dir = mms_dir

    def download_func(remote_base_url, local_base_dir, directory,
                      fname, remote_fname, extension):
        remote_url = remote_base_url + str(directory)
        util.load(fname + extension,
                  local_base_dir / directory,
                  remote_url)

    def processing_func(cdf):
        df = util.cdf2df(cdf, 'Epoch')
        return df

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)
