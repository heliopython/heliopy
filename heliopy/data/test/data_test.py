import heliopy.data.wind as wind
from datetime import datetime
import urllib


def test_wind():
    """
    Tests for imporitng wind data.

    Currently only try to download a single day's data for each product.
    """
    starttime = datetime(2010, 1, 1, 0, 0, 0)
    endtime = datetime(2010, 1, 1, 23, 59, 59)

    wind.mfi_h0(starttime, endtime)
    wind.threedp_pm(starttime, endtime)
