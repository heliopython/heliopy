import heliopy.data.wind as wind
import heliopy.data.mms as mms
import heliopy.data.helios as helios
import heliopy.data.cluster as cluster
import heliopy.data.ace as ace
import heliopy.data.artemis as artemis
import heliopy.data.imp as imp
import heliopy.data.ulysses as ulysses
import heliopy.data.messenger as messenger
from heliopy import config

from datetime import datetime
import urllib
import pytest


nodata = pytest.mark.skipif(
    pytest.config.getoption("--no-data"),
    reason="Skipped test that involves data download"
)


@nodata
def test_messenger():
    starttime = datetime(2010, 1, 1, 0, 0, 0)
    endtime = datetime(2010, 1, 2, 1, 0, 0)
    messenger.mag_rtn(starttime, endtime)


@nodata
def test_ulysses():
    starttime = datetime(1993, 1, 1, 0, 0, 0)
    endtime = datetime(1993, 1, 2, 0, 0, 0)
    ulysses.fgm_hires(starttime, endtime)
    ulysses.swoops_ions(starttime, endtime)


@nodata
def test_artemis():
    starttime = datetime(2008, 1, 1, 0, 0, 0)
    endtime = datetime(2008, 1, 2, 0, 0, 0)
    probe = 'a'
    artemis.fgm(probe, 'h', 'dsl', starttime, endtime)


@nodata
def test_ace():
    starttime = datetime(2016, 1, 1, 0, 0, 0)
    endtime = datetime(2016, 1, 2, 0, 0, 0)
    ace.mfi_h0(starttime, endtime)


@nodata
def test_imp():
    starttime = datetime(1976, 1, 1, 0, 0, 0)
    endtime = datetime(1976, 1, 2, 0, 0, 0)
    imp.mag320ms('8', starttime, endtime)
    imp.mitplasma_h0('8', starttime, endtime)


@nodata
def test_cluster():
    if config['DEFAULT']['cluster_cookie'] != 'none':
        probe = '2'
        starttime = datetime(2004, 6, 18, 11, 35, 0)
        endtime = datetime(2004, 6, 19, 18, 35, 0)
        cluster.fgm(probe, starttime, endtime)

        starttime = datetime(2009, 12, 22, 4, 0, 0)
        endtime = datetime(2009, 12, 22, 6)
        cluster.peace_moments(probe, starttime, endtime)

        probe = '3'
        starttime = datetime(2009, 1, 1, 0, 0, 0)
        endtime = datetime(2009, 1, 1, 2, 0, 0)
        cluster.cis_hia_onboard_moms(probe, starttime, endtime)


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
    wind.swe_h3(starttime, endtime)


@nodata
def test_mms():
    """
    Tests for importing mms data.

    Try and import a single days' worth of data for each data product.
    """
    starttime = datetime(2016, 1, 2, 0, 0, 0)
    endtime = datetime(2016, 1, 2, 1, 0, 0)

    probe = '1'
    mms.fgm_survey(probe, starttime, endtime)
    mms.fpi_dis_moms(probe, 'fast', starttime, endtime)


@nodata
def test_helios():
    """
    Tests for importing Helios data.

    Try and import a single days' worth of data for each data product.
    """
    starttime = datetime(1976, 1, 1, 0, 0, 0)
    endtime = datetime(1976, 1, 1, 23, 59, 59)
    helios.merged('1', starttime, endtime)
