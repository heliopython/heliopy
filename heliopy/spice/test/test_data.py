import os

import requests
import pytest

from heliopy import spice
from heliopy.spice import data as spicedata


@pytest.mark.parametrize('kernel_name', spicedata.kernel_dict)
def test_kernel_urls(kernel_name):
    urls = list(spicedata.kernel_dict[kernel_name].urls)
    for url in urls:
        if url[:3] == 'ftp':
            pytest.xfail("Requests can't handle FTP requests")
        with requests.get(url) as r:
            r.raise_for_status()


def test_kernel_download():
    # Test download
    kernel = spicedata.get_kernel('helios1')[0]

    # Check that kernel is valid
    if isinstance(kernel, spice.SPKKernel):
        kernel.bodies
