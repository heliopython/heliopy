"""
Methods for importing data from the four MMS spacecraft.

The MMS science data centre
is at https://lasp.colorado.edu/mms/sdc/public/.
"""
import os
import pathlib
import requests
from tqdm.auto import tqdm
from datetime import datetime, timedelta

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
                           'edp', 'fgm', 'fpi', 'fields', 'scm', 'sdp', 'mec']
    if instrument not in allowed_instruments:
        raise ValueError(
            'Instrument {} not in list of allowed instruments: {}'.format(
                instrument, allowed_instruments))


def _validate_probe(probe):
    allowed_probes = [str(i + 1) for i in range(4)]
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


def available_files(probe, instrument, starttime, endtime, data_rate='',
                    product_string=''):
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
    starttime : ~datetime.datetime
        Start time.
    endtime : ~datetime.datetime
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
    if starttime.date() == endtime.date():
        end_date = (endtime.date() + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        end_date = endtime.strftime('%Y-%m-%d')

    query = {}
    query['sc_id'] = 'mms' + probe
    query['instrument_id'] = instrument
    if len(data_rate):
        query['data_rate_mode'] = data_rate
    if len(product_string):
        query['descriptor'] = product_string
    query['start_date'] = start_date
    query['end_date'] = end_date

    r = requests.get(query_url, params=query)
    files = r.text.split(',')
    files = filter_time(files, starttime, endtime)
    return files


def filter_time(fnames, starttime, endtime):
    """
    Filter files by their start times.

    Parameters
    ----------
    fnames : str or list
        File names to be filtered.
    starttime : ~datetime.datetime
        Start date of time interval
    endtime : ~datetime.datetime
        End date of time interval

    Returns
    -------
        paths : list
            Path to the data file.
    """

    # Output
    files = fnames
    if isinstance(files, str):
        files = [files]

    # Parse the time out of the file name
    parts = parse_filename(fnames)
    fstart = [datetime.strptime(name[-2], '%Y%m%d') if len(name[-2]) == 8 else
              datetime.strptime(name[-2], '%Y%m%d%H%M%S')
              for name in parts]

    # Sort the files by start time
    isort = sorted(range(len(fstart)), key=lambda k: fstart[k])
    fstart = [fstart[i] for i in isort]
    files = [files[i] for i in isort]

    # End time
    #   - Any files that start on or before END_DATE can be kept
    idx = [i for i, t in enumerate(fstart) if t <= endtime]
    if len(idx) > 0:
        fstart = [fstart[i] for i in idx]
        files = [files[i] for i in idx]
    else:
        fstart = []
        files = []

    # Start time
    #   - Any file with TSTART <= START_DATE can potentially have data
    #     in our time interval of interest.
    #   - Assume the start time of one file marks the end time of the
    #     previous file.
    #   - With this, we look for the file that begins just prior to
    #     START_DATE and throw away any files that start before it.
    idx = [i for i, t in enumerate(fstart) if t >= starttime]

    if (len(idx) == 0) & (fstart[-1].date() == starttime.date()):
        idx = [len(fstart) - 1]
    elif (len(idx) != 0) & ((idx[0] != 0) & (fstart[idx[0]] != starttime)):
        idx.insert(0, idx[0] - 1)

    if len(idx) > 0:
        fstart = [fstart[i] for i in idx]
        files = [files[i] for i in idx]
    else:
        fstart = []
        files = []

    return files


def parse_filename(fnames):
    """
    Construct a file name compliant with MMS file name format guidelines.

    Parameters
    ----------
    fname : str or list
        File names to be parsed.

    Returns
    -------
    parts : list
        A list of tuples. The tuple elements are:
            [0]: Spacecraft IDs
            [1]: Instrument IDs
            [2]: Data rate modes
            [3]: Data levels
            [4]: Optional descriptor (empty string if not present)
            [5]: Start times
            [6]: File version number
    """

    # Allocate space
    out = []

    if type(fnames) is str:
        files = [fnames]
    else:
        files = fnames

    # Parse each file
    for file in files:
        # Parse the file names
        parts = os.path.basename(file).split('_')

        if len(parts) == 6:
            optdesc = ''
        else:
            optdesc = parts[4]

        out.append((*parts[0:4], optdesc, parts[-2], parts[-1][1:-4]))

    return out


def download_files(probe, instrument, data_rate, starttime, endtime,
                   verbose=True, product_string='', warn_missing_units=True):
    """
    Download MMS files.

    Parameters
    ----------
    probe : int or str
        MMS probe number. Must be in 1-4 inclusive.
    instrument : str
        MMS instrument. Must be in ``['afg', 'aspoc', 'dfg', 'dsp', 'edi',
        'edp', 'fields', 'scm', 'sdp']``
    data_rate : str
        Data rate. Must be in ``['slow', 'fast', 'brst', 'srvy']``
    starttime : ~datetime.datetime
        Start time.
    endtime : ~datetime.datetime
        End time.
    verbose : bool, optional
        If ``True``, show a progress bar while downloading.
    product_string : str, optional
        If not empty, this string must be in the filename for it to be
        downloaded.
    warn_missing_units : bool, optional
        If ``True``, warnings will be shown for each variable that does not
        have associated units.

    Returns
    -------
    df : :class:`~sunpy.timeseries.GenericTimeSeries`
        Requested data.
    """
    _validate_instrument(instrument)
    probe = _validate_probe(probe)

    dirs = []
    fnames = []
    daylist = util._daysplitinterval(starttime, endtime)
    for date, stime, etime in daylist:
        files = available_files(probe, instrument, starttime, endtime,
                                data_rate, product_string)
        for file in files:
            fname = pathlib.Path(file).stem
            if product_string in fname and len(fname):
                fnames.append(fname)
                dirs.append('')

    extension = '.cdf'
    local_base_dir = mms_dir / probe / instrument / data_rate
    remote_base_url = dl_url

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        url = remote_base_url + '?file=' + fname + extension
        local_fname = os.path.join(local_base_dir, fname + extension)
        with requests.get(url, stream=True) as request:
            with open(local_fname, 'wb') as fd:
                for chunk in tqdm(
                        request.iter_content(chunk_size=128)):
                    fd.write(chunk)

    def processing_func(cdf):
        return util.cdf2df(cdf, index_key='Epoch')

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime,
                        warn_missing_units=warn_missing_units)


def _fpi_docstring(product):
    return """
Import fpi {} data.

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
""".format(product)


def fpi_dis_moms(probe, mode, starttime, endtime):
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='dis-moms')


fpi_dis_moms.__doc__ = _fpi_docstring('ion distribution moment')


def fpi_des_moms(probe, mode, starttime, endtime):
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='des-moms')


fpi_des_moms.__doc__ = _fpi_docstring('electron distribution moment')


def fpi_dis_dist(probe, mode, starttime, endtime):
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='dis-dist', warn_missing_units=False)


fpi_dis_dist.__doc__ = _fpi_docstring('ion distribution function')


def fpi_des_dist(probe, mode, starttime, endtime):
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='des-dist', warn_missing_units=False)


fpi_des_dist.__doc__ = _fpi_docstring('electron distribution function')


def fgm(probe, mode, starttime, endtime):
    """
    Import fgm survey mode magnetic field data.

    Parameters
    ----------
    probe : string
        Probe number, must be 1, 2, 3, or 4
    mode : str
        Data rate.
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Imported data.
    """
    return download_files(probe, 'fgm', mode, starttime, endtime)
