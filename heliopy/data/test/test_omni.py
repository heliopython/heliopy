from datetime import datetime
import pytest

from .util import check_data_output_ts
from .util import check_data_output_xr

omni = pytest.importorskip('heliopy.data.omni')
pytest.mark.data()


starttime = datetime(1970, 1, 1, 0, 0, 0)
endtime = datetime(1970, 1, 2, 0, 0, 0)


def test_low_ts():
    data = omni.low(starttime, endtime)
    check_data_output_ts(data)
    
def test_low_xr():
    data = omni.low(starttime, endtime, want_xr=True)
    check_data_output_xr(data)
