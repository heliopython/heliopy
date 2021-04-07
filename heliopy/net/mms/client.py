"""
MMS client
~~~~~~~~~~
The MMS client indexes the MMS Science Data Center.

Searching using this client requires the both the `~heliopy.net.attrs.Time`
and `~heliopy.net.attrs.Source` (specifically ``Source('MMS')``) to be
specified. In addition, any of these attributes can be specified to narrow
the search:

- `~heliopy.net.attrs.Probe`
- `~heliopy.net.attrs.Instrument`
- `~heliopy.net.attrs.DataRate`
- `~heliopy.net.attrs.Level`
- `~heliopy.net.attrs.Version`

For descriptions of valid values for these attributes, see
https://lasp.colorado.edu/mms/sdc/public/about/how-to/
"""


import pathlib

import requests

import astropy.table
from astropy.time import Time
from sunpy.net.base_client import BaseClient, QueryResponseTable
from sunpy.net.attr import and_

from heliopy.net.mms.walker import walker
import heliopy.net.attrs as a

__all__ = ['MMSClient']


class MMSClient(BaseClient):
    """
    MMS client.
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
        required = {a.Time, a.Source}
        query_attrs = {type(x) for x in query}
        return query_attrs >= required

    @classmethod
    def register_values(cls):
        adict = {a.Instrument: [('afg', ''),
                                ('aspoc', ''),
                                ('dfg', ''),
                                ('dsp', ''),
                                ('edi', ''),
                                ('edp', ''),
                                ('fields', ''),
                                ('scm', ''),
                                ('sdp', '')],
                 a.Source: [('MMS', 'Magnetospheric Multiscale Mission')],
                 a.Provider: [('MMS SDC', 'MMS Science Data Center')],
                 a.Level: [('l1a', ''),
                           ('l1b', ''),
                           ('l2', ''),
                           ('ql', '')],
                 a.Probe: [('1', 'MMS1'),
                           ('2', 'MMS2'),
                           ('3', 'MMS3'),
                           ('4', 'MMS4')]}
        return adict
