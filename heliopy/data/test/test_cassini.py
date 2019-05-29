from datetime import datetime
import pytest
from .util import check_data_output

pytest.mark.data()
cassini = pytest.importorskip("heliopy.data.cassini")


def test_mag_hires():
    starttime = datetime(2008, 6, 1, 0, 0, 0)
    endtime = datetime(2008, 6, 2, 1, 0, 0)
    df = cassini.mag_hires(starttime, endtime)
    check_data_output(df)

    # Check that a RTN co-ordinate download works too
    starttime = datetime(2004, 5, 1)
    endtime = datetime(2004, 5, 2)
    df = cassini.mag_hires(starttime, endtime)
    check_data_output(df)

    # Check that no data raises an error
    starttime = datetime(2040, 5, 1)
    endtime = datetime(2040, 5, 2)
    with pytest.raises(RuntimeError):
        df = cassini.mag_hires(starttime, endtime)


def test_mag_1min():
    starttime = datetime(2008, 6, 1, 0, 0, 0)
    endtime = datetime(2008, 6, 2, 1, 0, 0)
    df = cassini.mag_1min(starttime, endtime, 'KSO')
    check_data_output(df)
