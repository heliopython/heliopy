from datetime import datetime
import pytest
from .util import check_data_output

cassini = pytest.importorskip("heliopy.data.cassini")
pytestmark = pytest.mark.data


@pytest.mark.skip("Cassini tests do not work on CI")
def test_mag_hires():
    starttime = datetime(2002, 2, 1)
    endtime = datetime(2002, 2, 1, 1)
    df = cassini.mag_hires(starttime, endtime)
    check_data_output(df)

    # Check that a RTN co-ordinate download works too
    starttime = datetime(2001, 1, 1)
    endtime = datetime(2001, 1, 1, 23)
    df = cassini.mag_hires(starttime, endtime)
    check_data_output(df)

    # Check that no data raises an error
    starttime = datetime(2040, 5, 1)
    endtime = datetime(2040, 5, 2)
    with pytest.raises(RuntimeError):
        df = cassini.mag_hires(starttime, endtime)


@pytest.mark.skip("Cassini tests do not work on CI")
def test_mag_1min():
    starttime = datetime(2008, 6, 1)
    endtime = datetime(2008, 6, 2, 23)
    df = cassini.mag_1min(starttime, endtime, 'KSO')
    check_data_output(df)
