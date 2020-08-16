"""
Methods for importing data from Solar Orbiter.
"""
import urllib
import urllib.parse
import pathlib

import requests
from heliopy.data import util
from heliopy.data import helper
from sunpy import time


class _SoloDownloader(util.Downloader):
    base_url = 'http://soar.esac.esa.int/soar-sl-tap/data?'

    def __init__(self, instrument, level):
        """
        Parameters
        ----------
        level : str
            One of ``['TELEMETRY', 'PLANNING', 'LOW_LATENCY']``.
        """
        self.level = level
        self.instrument = instrument

    def intervals(self, starttime, endtime):
        base_url = 'http://soar.esac.esa.int/soar-sl-tap/tap/sync?REQUEST=doQuery&'
        begin_time = time.parse_time(starttime).isot.replace('T', '+')
        end_time = time.parse_time(endtime).isot.replace('T', '+')
        # Need to manually set the intervals based on a query
        # QUERY=SELECT+*+FROM+v_data_item+WHERE+instrument=%27MAG%27+AND+level=%27LL02%27+AND+begin_time%3E=%272020-08-02+00:00:00.000%27+AND+end_time%3C=%272020-08-04+00:00:00.000%27
        request_dict = {}
        request_dict['LANG'] = 'ADQL'
        request_dict['FORMAT'] = 'json'

        query = {}
        query['SELECT'] = '*'
        query['FROM'] = 'v_data_item'
        query['WHERE'] = f"instrument='{self.instrument}'+AND+level='{self.level}'+AND+begin_time<='{end_time}'+AND+end_time>='{begin_time}'"
        request_dict['QUERY'] = '+'.join([f'{item}+{query[item]}' for item in query])

        request_str = ''
        request_str = [f'{item}={request_dict[item]}' for item in request_dict]
        request_str = '&'.join(request_str)

        url = base_url + request_str
        # Get request info
        r = requests.get(url)

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
        self.file_ids = {interval.start.isot: id for interval, id in zip(intervals, info['data_item_id'])}
        # TODO: log the number of intervals found here
        return intervals

    def _file_id(self, interval):
        return self.file_ids[interval.start.isot]

    def download(self, interval):
        base_url = 'http://soar.esac.esa.int/soar-sl-tap/data?retrieval_type=PRODUCT&product_type=LOW_LATENCY&data_item_id='
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
        return pathlib.Path('solar_orbiter')

    def fname(self, interval):
        return f'{self._file_id(interval)}.cdf'


def download(starttime, endtime, instrument, level):
    instrument = instrument.upper()
    helper._check_in_list(['MAG'], instrument=instrument)

    level = level.upper()
    helper._check_in_list(['LL02'], level=level)

    dl = _SoloDownloader(instrument, level)
    return dl.load(starttime, endtime)
