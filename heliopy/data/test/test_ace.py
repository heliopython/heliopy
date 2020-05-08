from datetime import datetime
import pytest

from .util import check_data_output

ace = pytest.importorskip('heliopy.data.ace')
pytestmark = pytest.mark.data

starttime = datetime(2010, 1, 1, 0, 0, 0)
endtime = datetime(2010, 1, 2, 0, 0, 0)


def test_swi_h3b():
    df = ace.swi_h3b(datetime(2013, 1, 1), datetime(2013, 1, 1, 12))
    check_data_output(df)


# No data currently available?
'''
def test_swi_h4():
    df = ace.swi_h4(starttime, endtime + timedelta(days=2))
    check_data_output(df)
'''


@pytest.mark.parametrize('f', [ace.swi_h5, ace.mfi_h1, ace.mfi_h2, ace.mfi_h3,
                               ace.swe_h0, ace.swe_h2, ace.swi_h2, ace.swi_h3,
                               ace.swi_h6, ace.mfi_h0])
def test_ace(f):
    df = f(starttime, endtime)
    check_data_output(df)
