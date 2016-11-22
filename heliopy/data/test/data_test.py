import heliopy.data.wind as wind
from datetime import datetime


def test_mfi_h0():
    starttime = datetime(2010, 1, 1, 0, 0, 0)
    endtime = datetime(2010, 1, 1, 23, 59, 59)
    wind.mfi_h0(starttime, endtime)
