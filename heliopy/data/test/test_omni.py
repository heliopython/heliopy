from datetime import datetime
import pytest

from heliopy.data import omni
from .util import check_data_output

pytestmark = pytest.mark.data
starttime = datetime(2000, 1, 1, 0, 0, 0)
endtime = datetime(2000, 1, 2, 0, 0, 0)


@pytest.mark.parametrize('f', [omni.h0_mrg1hr])
def test_omni(f):
    df = f(starttime, endtime)
    check_data_output(df)
