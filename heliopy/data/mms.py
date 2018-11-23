"""
Methods for importing data from the four MMS spacecraft.

All data is publically available at
https://lasp.colorado.edu/mms/sdc/public/data/, and the MMS science data centre
is at https://lasp.colorado.edu/mms/sdc/public/.
"""
from datetime import datetime
import numpy as np
import pandas as pd
import pathlib as path
from collections import OrderedDict
import astropy.units as u
import requests

from heliopy.data import util
from heliopy import config

data_dir = path.Path(config['download_dir'])
mms_dir = data_dir / 'mms'
mms_url = 'https://lasp.colorado.edu/mms/sdc/public'
remote_mms_dir = mms_url + '/data/'
query_url = mms_url + '/files/api/v1/file_names/science'


def _validate_instrument(instrument):
    allowed_instruments = ['afg', 'aspoc', 'dfg', 'dsp', 'edi',
                           'edp', 'fields', 'scm', 'sdp']
    if instrument not in allowed_instruments:
        raise ValueError(
            'Instrument {} not in list of allowed instruments: {}'.format(
                instrument, allowed_instrument))


def _validate_probe(probe):
    allowed_probes = [str(i) for i in range(4)]
    probe = str(probe)
    if probe not in allowed_probes:
        raise ValueError(
            'Probe {} not in list of allowed probes: {}'.format(
                probe, allowed_probes))
    return probe


def _validate_data_rate(data_rate):
    allowed_rates = ['slow', 'fast', 'brst', 'srvy']
    if data_rate not in allowed_rates:
        raise ValueError(
            'Data rate {} not in list of allowed data rates: {}'.format(
                data_rate, allowed_rates))


def mms_available_files(probe, instrument, data_rate, starttime, endtime):
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
    """
    _validate_instrument(instrument)
    probe = _validate_probe(probe)
    _validate_data_rate(data_rate)
    start_date = starttime.strftime('%Y-%m-%d')
    end_date = endtime.strftime('%Y-%m-%d')

    query = {}
    query['sc_id'] = 'mms' + probe
    query['instrument_id'] = instrument
    query['data_rate_mode'] = data_rate
    query['start_date'] = start_date
    query['end_date'] = end_date

    r = requests.get(query_url, params=query)
    files = r.text.split(',')
    return files


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
    valid_modes = ['fast', 'brst']
    if mode not in valid_modes:
        raise RuntimeError('Mode must be either fast or brst')
    # Directory relative to main MMS data directory
    relative_dir = path.Path('mms' + probe) / 'fpi' / mode / 'l2' / 'dis-moms'
    dirs = []
    fnames = []
    daylist = util._daysplitinterval(starttime, endtime)
    units = OrderedDict([('mms{}_dis_errorflags_fast'.format(probe),
                          u.dimensionless_unscaled),
                         ('mms{}_dis_startdelphi_count_fast'.format(probe),
                          u.dimensionless_unscaled)])

    extension = '.cdf'

    for day in daylist:
        date = day[0]
        starthour = day[1].hour
        endhour = day[2].hour + 1
        # fips fast data product has files every two hours, so get nearest two
        # hour stamps
        starthour -= np.mod(starthour, 2)
        endhour += np.mod(endhour, 2)
        for h in range(starthour, endhour, 2):
            this_relative_dir = (relative_dir /
                                 str(date.year) /
                                 str(date.month).zfill(2))
            filename = ('mms{}_fpi_{}_l2_dis-moms_'
                        '{}{:02}{:02}{:02}0000_v3.3.0').format(
                            probe, mode, date.year, date.month, date.day, h)
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
        probestr = 'mms' + probe + '_'
        df = util.cdf2df(cdf, 'Epoch')
        return df

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)


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
    valid_modes = ['fast', 'brst']
    if mode not in valid_modes:
        raise RuntimeError('Mode must be either fast or brst')
    # Directory relative to main MMS data directory
    relative_dir = path.Path('mms' + probe) / 'fpi' / mode / 'l2' / 'des-moms'
    dirs = []
    fnames = []
    daylist = util._daysplitinterval(starttime, endtime)
    data = []
    units = OrderedDict([('mms{}_des_errorflags_fast'.format(probe),
                          u.dimensionless_unscaled),
                         ('mms{}_des_startdelphi_count_fast'.format(probe),
                          u.dimensionless_unscaled)])

    extension = '.cdf'

    for day in daylist:
        date = day[0]
        starthour = day[1].hour
        endhour = day[2].hour + 1
        # fips fast data product has files every two hours, so get nearest two
        # hour stamps
        starthour -= np.mod(starthour, 2)
        endhour += np.mod(endhour, 2)
        for h in range(starthour, endhour, 2):
            this_relative_dir = (relative_dir /
                                 str(date.year) /
                                 str(date.month).zfill(2))
            filename = ('mms{}_fpi_{}_l2_des-moms_'
                        '{}{:02}{:02}{:02}0000_v3.3.0').format(
                            probe, mode, date.year, date.month, date.day, h)
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
        probestr = 'mms' + probe + '_'
        df = util.cdf2df(cdf, 'Epoch')
        return df

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)


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
    relative_dir = path.Path('mms' + probe) / 'fgm' / 'srvy' / 'l2'
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
