from sunpy.net import Fido
import pytest

import heliopy.net.attrs as a


pytestmark = pytest.mark.data


def test_query():
    query = (a.Time('2018-11-01', '2018-11-01 01:00:00') &
             a.Source('MMS') &
             a.Version('2.0.3'))
    res = Fido.search(query)
    assert len(res) == 1
    assert len(res[0]) == 4

    files = Fido.fetch(res)
    assert len(files) == 4
