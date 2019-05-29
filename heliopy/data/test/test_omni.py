from datetime import datetime
import pytest

from .util import check_data_output

omni = pytest.importorskip('heliopy.data.omni')
pytest.mark.data()


starttime = datetime(1970, 1, 1, 0, 0, 0)
endtime = datetime(1970, 1, 2, 0, 0, 0)


def test_low():
    df = omni.low(starttime, endtime)
    check_data_output(df)
