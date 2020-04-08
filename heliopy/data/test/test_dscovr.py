from datetime import datetime
import pytest

from .util import check_data_output

dscovr = pytest.importorskip('heliopy.data.dscovr')
pytestmark = pytest.mark.data

starttime = datetime(2015, 6, 8, 0, 0, 0)
endtime = datetime(2015, 6, 9, 0, 0, 0)


def test_mag_h0():
    df = dscovr.mag_h0(starttime, endtime)
    check_data_output(df)
