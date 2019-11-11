from datetime import datetime
import pytest
from .util import check_data_output

pytest.mark.data()
cassini = pytest.importorskip("heliopy.data.cassini")


def test_mag_1min():
    starttime = datetime(2008, 6, 1, 0, 0, 0)
    endtime = datetime(2008, 6, 2, 1, 0, 0)
    df = cassini.mag_1min(starttime, endtime, 'KSO')
    check_data_output(df)
