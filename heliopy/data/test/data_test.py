import heliopy.data.wind as wind
import heliopy.data.mms as mms
import heliopy.data.helios as helios
import heliopy.data.cluster as cluster
import heliopy.data.imp as imp
from heliopy import config

from datetime import datetime
import urllib
import pytest


nodata = pytest.mark.skipif(
    pytest.config.getoption("--no-data"),
    reason="Skipped test that involves data download"
)


@nodata
def test_imp():
    starttime = datetime(1976, 1, 1, 0, 0, 0)
    endtime = datetime(1976, 1, 2, 0, 0, 0)
    imp.mag320ms('8', starttime, endtime)


@nodata
def test_cluster():
    if config['cluster']['user_cookie'] != 'none':
        probe = '2'
        starttime = datetime(2004, 6, 18, 11, 35, 0)
        endtime = datetime(2004, 6, 19, 18, 35, 0)
        cluster.fgm(probe, starttime, endtime)


@nodata
def test_wind():
    """
    Tests for imporitng wind data.

    Currently only try to download a single day's data for each product.
    """
    starttime = datetime(2010, 1, 1, 0, 0, 0)
    endtime = datetime(2010, 1, 1, 23, 59, 59)

    wind.mfi_h0(starttime, endtime)
    wind.threedp_pm(starttime, endtime)


@nodata
def test_mms():
    """
    Tests for importing mms data.

    Try and import a single days' worth of data for each data product.
    """
    starttime = datetime(2016, 1, 1, 0, 0, 0)
    endtime = datetime(2016, 1, 1, 1, 0, 0)

    for i in range(1, 5):
        mms.fgm_survey(str(i), starttime, endtime)


@nodata
def test_helios():
    """
    Tests for importing Helios data.

    Try and import a single days' worth of data for each data product.
    """
    starttime = datetime(1976, 1, 1, 0, 0, 0)
    endtime = datetime(1976, 1, 1, 23, 59, 59)
    helios.merged('1', starttime, endtime)
