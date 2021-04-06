from sunpy.net import Fido
import pytest

import heliopy.net.attrs as a


pytestmark = pytest.mark.data


def test_query():
    res = Fido.search(a.Time('2018-11-01', '2018-11-01 01:00:00'),
                      a.Dataset('WI_H1_SWE') | a.Dataset('WI_H5_SWE'))
    assert len(res) == 2
    assert len(res[0]) == 1
    assert len(res[1]) == 2

    files = Fido.fetch(res)
    assert len(files) == 3
