import pathlib

import requests

import astropy.table
from astropy.time import Time
from sunpy.net.base_client import BaseClient, QueryResponseTable
from sunpy.net.attr import and_

import heliopy.net.attrs as a
from heliopy.net.cdaweb.walker import walker

__all__ = ['SPDFClient']

CDAS_BASEURL = 'https://cdaweb.gsfc.nasa.gov/WS/cdasr/1'
CDAS_HEADERS = {'Accept': 'application/json'}
CDAS_TIME_FMT = '%Y%m%dT%H%M%SZ'


class SPDFClient(BaseClient):
    def search(self, *query, **kwargs):
        """
        Search for datasets provided by the Space Physics Data Facility.
        """
        query = and_(*query)
        queries = walker.create(query)

        results = []
        for query_parameters in queries:
            results.append(self._do_search(query_parameters))
        table = astropy.table.vstack(results)
        qrt = QueryResponseTable(table, client=self)
        qrt.hide_keys = ['URL']
        return qrt

    def _do_search(self, query):
        response = (self._get_remote_files(query['dataset'],
                                           query['begin_time'],
                                           query['end_time']))

        if 'FileDescription' not in response:
            raise RuntimeError

        stimes = [f['StartTime'] for f in response['FileDescription']]
        etimes = [f['EndTime'] for f in response['FileDescription']]
        urls = [f['Name'] for f in response['FileDescription']]

        return astropy.table.QTable(
            {'Dataset': [query['dataset']] * len(stimes),
             'Start time': Time.strptime(stimes, '%Y-%m-%dT%H:%M:%S.%fZ').iso,
             'End time': Time.strptime(etimes, '%Y-%m-%dT%H:%M:%S.%fZ').iso,
             'URL': urls})

    @staticmethod
    def _get_remote_files(dataset, start, end):
        dataview = 'sp_phys'
        start = start.strftime(CDAS_TIME_FMT)
        end = end.strftime(CDAS_TIME_FMT)
        url = '/'.join([
            CDAS_BASEURL,
            'dataviews', dataview,
            'datasets', dataset,
            'orig_data', f'{start},{end}'
        ])
        response = requests.get(url, headers=CDAS_HEADERS)
        return response.json()

    def fetch(self, query_results, *, path, downloader, **kwargs):
        for row in query_results:
            fname = row['URL'].split('/')[-1]
            filepath = str(path).format(file=fname)
            downloader.enqueue_file(row['URL'], filename=filepath)

    @classmethod
    def _can_handle_query(cls, *query):
        required = {a.Dataset, a.Time}
        query_attrs = {type(x) for x in query}
        return required == query_attrs
