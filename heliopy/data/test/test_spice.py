import os
import pytest

from heliopy import spice
from heliopy.data import spice as spicedata


@pytest.mark.parametrize('kernel', spicedata.kernel_dict)
def test_kernel_download(kernel):
    if 'TRAVIS' in os.environ:
        for url in spicedata.kernel_dict[kernel].urls:
            if url[:3] == 'ftp':
                pytest.skip("FTP doesn't work on travis")
    if 'AZURE' in os.environ and 'psp' in kernel:
        pytest.skip("PSP kernels don't work on Azure")

    # Test download
    with pytest.warns(None) as record:
        kernel = spicedata.get_kernel(kernel)[0]
    assert len(record) == 0

    # Check that kernel is valid
    if isinstance(kernel, spice.SPKKernel):
        kernel.bodies
