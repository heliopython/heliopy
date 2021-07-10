from datetime import datetime
import pytest

from .util import check_data_output

voyager = pytest.importorskip('heliopy.data.voyager')
pytestmark = pytest.mark.data

starttime = datetime(2010, 1, 1, 0, 0, 0)
endtime = datetime(2010, 1, 1, 23, 59, 59)


def test_voyager1_merged():
    df = voyager.voyager1_merged(starttime, endtime)
    check_data_output(df)
