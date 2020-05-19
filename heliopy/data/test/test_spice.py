import os
import pytest
from heliopy.data import spice


@pytest.mark.data
@pytest.mark.parametrize('kernel', spice.kernel_dict)
def test_kernel_download(kernel):
    if 'TRAVIS' in os.environ:
        for url in spice.kernel_dict[kernel].urls:
            if url[:3] == 'ftp':
                pytest.skip("FTP doesn't work on travis")
    if 'AZURE' in os.environ and 'psp' in kernel:
        pytest.skip("PSP kernels don't work on Azure")
    with pytest.warns(None) as record:
        spice.get_kernel(kernel)
    assert len(record) == 0
