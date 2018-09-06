"""
Helper methods for using the CDAS REST web services.

For more information see https://cdaweb.sci.gsfc.nasa.gov/WebServices/REST/
"""
from datetime import datetime, time
import requests
import tempfile
import wget

import heliopy.data.util as util

CDAS_BASEURL = 'https://cdaweb.gsfc.nasa.gov/WS/cdasr/1'
CDAS_HEADERS = {'Accept': 'application/json'}


def get_variables(dataset):
    """
    Queries server for descriptions of variables in a dataset.

    Parameters
    ----------
    dataset : string
        Dataset identifier.

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
    response = requests.get(url, headers=CDAS_HEADERS)
    return response.json()


def get_data(dataset, date, vars=None, verbose=True):
    """
    Download CDAS data.

    Parameters
    ----------
    dataset : string
        Dataset identifier.
    date : datetime.date
        Date to download data for.
    vars : list of str, optional
        Variables to download. If ``None``, all variables for the given
        dataset will be downloaded.
    verbose : bool, optional
        If ``True``, show a progress bar whilst downloading.

    Returns
    -------
    data_path : str
        Path to downloaded data (stored in a temporary directroy)
    """
    starttime = datetime.combine(date, time.min)
    endtime = datetime.combine(date, time.max)
    dataview = 'sp_phys'
    if vars is not None:
        var_info = get_variables(dataset)
        vars = [v['Name'] for v in var_info['VariableDescription']]
    uri = '/'.join(['dataviews', dataview,
                    'datasets', dataset,
                    'data',
                    ','.join([starttime.strftime('%Y%m%dT%H%M%SZ'),
                              endtime.strftime('%Y%m%dT%H%M%SZ')]),
                    ','.join(vars)
                    ])
    url = '/'.join([CDAS_BASEURL, uri])
    params = {}
    ext = ''
    params = {'format': 'cdf', 'cdfVersion': 3}
    ext = 'cdf'
    response = requests.get(url, params=params, headers=CDAS_HEADERS)
    if 'FileDescription' in response.json():
        data_path = wget.download(
            response.json()['FileDescription'][0]['Name'],
            tempfile.gettempdir(),
            bar=wget.bar_adaptive if verbose else None
        )
        if verbose:
            print('')
    else:
        raise util.NoDataError
    return data_path
