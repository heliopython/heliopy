from datetime import datetime
import pytest
from .util import check_data_output
pytest.mark.data()
messenger = pytest.importorskip('heliopy.data.messenger')


def test_mag():
    starttime = datetime(2010, 1, 1, 0, 0, 0)
    endtime = datetime(2010, 1, 2, 1, 0, 0)
    df = messenger.mag_rtn(starttime, endtime)
    check_data_output(df)
