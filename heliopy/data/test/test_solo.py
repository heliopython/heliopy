from datetime import datetime
import pytest

from heliopy.data import solo

from .util import check_data_output

pytestmark = pytest.mark.data

starttime = datetime(2020, 8, 1)
endtime = datetime(2020, 8, 2)


def test_solo():
    df = solo.download(starttime, endtime, 'MAG', 'LL02')
    check_data_output(df)
