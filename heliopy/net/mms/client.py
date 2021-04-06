import pathlib

import requests

import astropy.table
from astropy.time import Time
from sunpy.net.base_client import BaseClient, QueryResponseTable
from sunpy.net.attr import and_
import sunpy.net.attrs as sunpy_attrs

from heliopy.net.mms.attrs import walker

__all__ = ['MMSClient']


class MMSClient(BaseClient):
    """
    MMS client.

    See https://lasp.colorado.edu/mms/sdc/public/about/how-to/.
    """
    _mms_url = 'https://lasp.colorado.edu/mms/sdc/public'
    _query_url = f'{_mms_url}/files/api/v1/file_names/science'
    _dl_url = f'{_mms_url}/files/api/v1/download/science'

    def search(self, *query, **kwargs):
        query = and_(*query)
        queries = walker.create(query)

        results = []
        for query_parameters in queries:
            results.append(self._do_search(query_parameters))
        table = astropy.table.vstack(results)
        qrt = QueryResponseTable(table, client=self)
        qrt.hide_keys = ['File']
        return qrt

    def _do_search(self, query):
        """
        Do a single search and return a list of files.
        """
        r = requests.get(self._query_url, params=query)
        if r.text:
            files = r.text.split(',')
            filenames = [f.split('/')[-1] for f in files]
        else:
            filenames = []
        return astropy.table.QTable({'Filename': filenames})

    def fetch(self, query_results, *, path, downloader, **kwargs):
        for row in query_results:
            filepath = str(path).format(file=row['Filename'])
            file = row['Filename']
            url = f'{self._dl_url}?file={file}'
            downloader.enqueue_file(url, filename=filepath)

    @classmethod
    def _can_handle_query(cls, *query):
        required = {sunpy_attrs.Time, sunpy_attrs.Source}
        query_attrs = {type(x) for x in query}
        return query_attrs >= required
