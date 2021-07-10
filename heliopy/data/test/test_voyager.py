from datetime import datetime
import pytest

from .util import check_data_output

voyager = pytest.importorskip('heliopy.data.voyager')
pytestmark = pytest.mark.data

starttime = datetime(1990, 1, 1)
endtime = datetime(1990, 5, 1)


def test_voyager1_merged():
    df = voyager.voyager1_merged(starttime, endtime)
    check_data_output(df)


def test_voyager2_merged():
    df = voyager.voyager2_merged(starttime, endtime)
    check_data_output(df)
