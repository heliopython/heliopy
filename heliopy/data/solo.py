"""
Methods for importing data from Solar Orbiter.
"""
import urllib
import urllib.parse
import pathlib
import warnings

import requests
from heliopy.data import util
from heliopy.data import helper
from sunpy import time


class _SoloDownloader(util.Downloader):
    base_url = 'http://soar.esac.esa.int/soar-sl-tap/data?'

    def __init__(self, descriptor, level):
        """
        Parameters
        ----------
        """
        helper._check_in_list(['LL02'], level=level)
        self.level = level
        if self.level[:2] == 'LL':
            self.product_type = 'LOW_LATENCY'

        self.descriptor = descriptor

    def intervals(self, starttime, endtime):
        base_url = ('http://soar.esac.esa.int/soar-sl-tap/tap/'
                    'sync?REQUEST=doQuery&')
        begin_time = time.parse_time(starttime).isot.replace('T', '+')
        end_time = time.parse_time(endtime).isot.replace('T', '+')
        # Need to manually set the intervals based on a query
        request_dict = {}
        request_dict['LANG'] = 'ADQL'
        request_dict['FORMAT'] = 'json'

        query = {}
        query['SELECT'] = '*'
        query['FROM'] = 'v_data_item'
        query['WHERE'] = (f"descriptor='{self.descriptor}'+AND+"
                          f"level='{self.level}'+AND+"
                          f"begin_time<='{end_time}'+AND+"
                          f"end_time>='{begin_time}'")
        request_dict['QUERY'] = '+'.join([f'{item}+{query[item]}' for
                                          item in query])

        request_str = ''
        request_str = [f'{item}={request_dict[item]}' for item in request_dict]
        request_str = '&'.join(request_str)

        url = base_url + request_str
        # Get request info
        r = requests.get(url)
        # TODO: intelligently detect and error on a bad descriptor

        # Do some list/dict wrangling
        names = [m['name'] for m in r.json()['metadata']]
        info = {name: [] for name in names}
        for entry in r.json()['data']:
            for i, name in enumerate(names):
                info[name].append(entry[i])

        # Setup intervals
        intervals = []
        for start, end in zip(info['begin_time'], info['end_time']):
            intervals.append(time.TimeRange(start, end))

        if len(intervals) == 0:
            raise RuntimeError(f'No data files found for '
                               f'descriptor={self.descriptor}, '
                               f'start_time={begin_time}, '
                               f'end_time={end_time}.')

        self.file_ids = {interval.start.isot: id for interval, id in
                         zip(intervals, info['data_item_id'])}
        # TODO: log the number of intervals found here
        return intervals

    def _file_id(self, interval):
        return self.file_ids[interval.start.isot]

    def download(self, interval):
        base_url = ('http://soar.esac.esa.int/soar-sl-tap/data?'
                    f'retrieval_type=PRODUCT&product_type={self.product_type}&'
                    'data_item_id=')
        url = base_url + self._file_id(interval)
        try:
            util._download_url(url, self.local_path(interval))
        except urllib.error.HTTPError:
            raise util.NoDataError

    def load_local_file(self, interval):
        local_path = self.local_path(interval)
        cdf = util._load_cdf(local_path)
        return util.cdf2df(cdf, index_key='EPOCH')

    def local_dir(self, interval):
        # TODO: work out how to be more granular than just solar orbiter
        return pathlib.Path('solar_orbiter') / self.descriptor / self.level

    def fname(self, interval):
        return f'{self._file_id(interval)}.cdf'


def download(starttime, endtime, descriptor, level):
    """
    starttime :
    endtime :
    descriptor : str
        One of ``['MAG']``.
    level : str
        One of ``['LL02']``.
    """
    descriptor = descriptor.upper()
    level = level.upper()
    dl = _SoloDownloader(descriptor, level)
    ret = dl.load(starttime, endtime)
    if level == 'LL02':
        url = ("https://www.cosmos.esa.int/web/solar-orbiter/"
               "access-to-solar-orbiter-low-latency-data")
        warnings.warn('Low latency data is not suitable for publication. '
                      f'See {url} for more information.')
    return ret
