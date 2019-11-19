"""
Helper methods for using the CDAS REST web services.

For more information see https://cdaweb.sci.gsfc.nasa.gov/WebServices/REST/
"""
import datetime as dt
import pathlib
import tempfile

import requests
import requests.exceptions
import sunpy.time as stime
import tqdm.auto as tqdm

import heliopy.data.util as util

CDAS_BASEURL = 'https://cdaweb.gsfc.nasa.gov/WS/cdasr/1'
CDAS_HEADERS = {'Accept': 'application/json'}


def _docstring(identifier, letter, description):
    ds = r"""
    {description} data.

    See https://cdaweb.sci.gsfc.nasa.gov/misc/Notes{letter}.html#{identifier}
    for more information.

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
    """.format(identifier=identifier,
               letter=letter,
               description=description)
    return ds


def _day_intervals(starttime, endtime):
    interval = stime.TimeRange(starttime, endtime)
    daylist = interval.get_dates()
    intervallist = [stime.TimeRange(t, t + dt.timedelta(days=1)) for
                    t in daylist]
    return intervallist


def _year_intervals(starttime, endtime):
    intervallist = []
    for year in range(starttime.year, endtime.year + 1):
        intervallist.append(stime.TimeRange(dt.datetime(year, 1, 1),
                                            dt.datetime(year + 1, 1, 1)))
    return intervallist


class CDASDownloader(util.Downloader):
    def __init__(self, dataset, identifier, dir, badvalues=None,
                 warn_missing_units=True, units=None, index_key='Epoch'):
        self.dataset = dataset
        self.identifier = identifier
        self.dir = dir
        self.badvalues = badvalues
        self.units = units
        self.warn_missing_units = warn_missing_units
        self.index_key = index_key

    @staticmethod
    def _interval_start(interval):
        stime = interval.start
        if not isinstance(stime, dt.datetime):
            stime = stime.to_datetime()
        return stime

    @staticmethod
    def _interval_end(interval):
        etime = interval.end
        if not isinstance(etime, dt.datetime):
            etime = etime.to_datetime()
        return etime

    @staticmethod
    def intervals(starttime, endtime):
        return _day_intervals(starttime, endtime)

    def fname(self, interval):
        stime = self._interval_start(interval)
        return '{}_{}_{}{:02}{:02}.cdf'.format(
            self.dataset, self.identifier, stime.year, stime.month, stime.day)

    def local_dir(self, interval):
        stime = self._interval_start(interval)
        return pathlib.Path(self.dir) / self.identifier / str(stime.year)

    def download(self, interval):
        stime = self._interval_start(interval)
        etime = self._interval_end(interval)
        return get_data(self.identifier, stime, etime)

    def load_local_file(self, interval):
        local_path = self.local_path(interval)
        cdf = util._load_cdf(local_path)
        return util.cdf2df(cdf, index_key=self.index_key,
                           badvalues=self.badvalues)


def get_variables(dataset, timeout=10):
    """
    Queries server for descriptions of variables in a dataset.

    Parameters
    ----------
    dataset : string
        Dataset identifier.
    timeout : float, optional
        Timeout on the CDAweb remote requests, in seconds. Defaults to 10s.

    Returns
    -------
    dict
        JSON response from the server.
    """
    dataview = 'sp_phys'
    url = '/'.join([
        CDAS_BASEURL,
        'dataviews', dataview,
        'datasets', dataset,
        'variables'
    ])
    response = requests.get(url, headers=CDAS_HEADERS, timeout=timeout)
    return response.json()


def get_cdas_url(starttime, endtime, vars, dataset, timeout=10):
    dataview = 'sp_phys'
    if vars is None:
        try:
            var_info = get_variables(dataset, timeout=timeout)
        except requests.exceptions.ReadTimeout:
            raise util.NoDataError(
                'Connection to CDAweb timed out when getting CDAS URL for '
                f'{dataset} data for interval {starttime} - {endtime}.')

        if not len(var_info):
            raise util.NoDataError(
                f'No {dataset} data available for date {date}')

        vars = [v['Name'] for v in var_info['VariableDescription']]

    uri = '/'.join(['dataviews', dataview,
                    'datasets', dataset,
                    'data',
                    ','.join([starttime.strftime('%Y%m%dT%H%M%SZ'),
                              endtime.strftime('%Y%m%dT%H%M%SZ')]),
                    ','.join(vars)
                    ])
    url = '/'.join([CDAS_BASEURL, uri])
    return url


def get_data(dataset, starttime, endtime, vars=None, timeout=100):
    """
    Download CDAS data.

    Parameters
    ----------
    dataset : string
        Dataset identifier.
    starttime : datetime.datetime
        Beginning of interval.
    endtime : datetime.datetime
        End of interval.
    vars : list of str, optional
        Variables to download. If ``None``, all variables for the given
        dataset will be downloaded.
    timeout : float, optional
        Timeout on the CDAweb remote requests, in seconds. Defaults to 10s.

    Returns
    -------
    data_path : str
        Path to downloaded data (stored in a temporary directroy)
    """
    url = get_cdas_url(starttime, endtime, vars, dataset, timeout=timeout)
    params = {'format': 'cdf', 'cdfVersion': 3}
    response = requests.get(
        url, params=params, headers=CDAS_HEADERS, timeout=timeout)

    if 'FileDescription' in response.json():
        print(f'Downloading {dataset} for interval {starttime} - {endtime}')
        url = response.json()['FileDescription'][0]['Name']
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            with requests.get(url, stream=True) as request:
                for chunk in tqdm.tqdm(request.iter_content(chunk_size=128)):
                    temp_file.write(chunk)

            return temp_file.name
    else:
        raise util.NoDataError(f'No {dataset} data available for interval '
                               f'{starttime} - {endtime}')
