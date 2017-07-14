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

import pandas as pd
from datetime import datetime
import urllib
import pytest


def check_datetime_index(df):
    'Helper funciton to check all dataframes have a datetime index'
    assert type(df.index[0]) == pd.Timestamp


@pytest.mark.data
def test_messenger():
    starttime = datetime(2010, 1, 1, 0, 0, 0)
    endtime = datetime(2010, 1, 2, 1, 0, 0)

    df = messenger.mag_rtn(starttime, endtime)
    check_datetime_index(df)


@pytest.mark.data
def test_ulysses():
    starttime = datetime(1993, 1, 1, 0, 0, 0)
    endtime = datetime(1993, 1, 2, 0, 0, 0)

    df = ulysses.fgm_hires(starttime, endtime)
    check_datetime_index(df)

    df = ulysses.swoops_ions(starttime, endtime)
    check_datetime_index(df)


@pytest.mark.data
def test_artemis():
    starttime = datetime(2008, 1, 1, 0, 0, 0)
    endtime = datetime(2008, 1, 2, 0, 0, 0)
    probe = 'a'
    df = artemis.fgm(probe, 'h', 'dsl', starttime, endtime)
    check_datetime_index(df)

    with pytest.raises(ValueError):
        artemis.fgm('123', 'h', 'dsl', starttime, endtime)
    with pytest.raises(ValueError):
        artemis.fgm('1', '123', 'dsl', starttime, endtime)
    with pytest.raises(ValueError):
        artemis.fgm('1', 'h', '123', starttime, endtime)


@pytest.mark.data
def test_ace():
    starttime = datetime(2016, 1, 1, 0, 0, 0)
    endtime = datetime(2016, 1, 2, 0, 0, 0)

    df = ace.mfi_h0(starttime, endtime)
    check_datetime_index(df)


@pytest.mark.data
def test_imp():
    starttime = datetime(1976, 1, 1, 0, 0, 0)
    endtime = datetime(1976, 1, 2, 0, 0, 0)
    df = imp.mag320ms('8', starttime, endtime)
    check_datetime_index(df)

    df = imp.mag15s('8', starttime, endtime)
    check_datetime_index(df)

    df = imp.mitplasma_h0('8', starttime, endtime)
    check_datetime_index(df)

    df = imp.merged('8', starttime, endtime)
    check_datetime_index(df)


@pytest.mark.data
def test_cluster():
    if config['DEFAULT']['cluster_cookie'] != 'none':
        probe = '2'
        starttime = datetime(2004, 6, 18, 11, 35, 0)
        endtime = datetime(2004, 6, 19, 18, 35, 0)
        df = cluster.fgm(probe, starttime, endtime)
        check_datetime_index(df)

        starttime = datetime(2009, 12, 22, 4, 0, 0)
        endtime = datetime(2009, 12, 22, 6)
        df = cluster.peace_moments(probe, starttime, endtime)
        check_datetime_index(df)

        probe = '3'
        starttime = datetime(2009, 1, 1, 0, 0, 0)
        endtime = datetime(2009, 1, 1, 2, 0, 0)
        df = cluster.cis_hia_onboard_moms(probe, starttime, endtime)
        check_datetime_index(df)

        df = cluster.cis_codif_h1_moms(probe, starttime, endtime)
        check_datetime_index(df)


@pytest.mark.data
def test_wind():
    """
    Tests for imporitng wind data.

    Currently only try to download a single day's data for each product.
    """
    starttime = datetime(2010, 1, 1, 0, 0, 0)
    endtime = datetime(2010, 1, 1, 23, 59, 59)

    df = wind.mfi_h0(starttime, endtime)
    check_datetime_index(df)

    df = wind.threedp_pm(starttime, endtime)
    check_datetime_index(df)

    df = wind.swe_h3(starttime, endtime)


@pytest.mark.data
def test_mms():
    """
    Tests for importing mms data.

    Try and import a single days' worth of data for each data product.
    """
    starttime = datetime(2016, 1, 2, 0, 0, 0)
    endtime = datetime(2016, 1, 2, 1, 0, 0)
    probe = '1'

    df = mms.fgm_survey(probe, starttime, endtime)
    check_datetime_index(df)

    df = mms.fpi_dis_moms(probe, 'fast', starttime, endtime)
    check_datetime_index(df)


@pytest.mark.data
class TestHelios:
    """Tests for importing Helios data."""
    def test_merged(self):
        starttime = datetime(1976, 1, 1, 0, 0, 0)
        endtime = datetime(1976, 1, 1, 23, 59, 59)
        df = helios.merged('1', starttime, endtime)
        check_datetime_index(df)

        starttime = datetime(2000, 1, 1, 0, 0, 0)
        endtime = datetime(2000, 1, 2, 0, 0, 0)
        for probe in ['1', '2']:
            with pytest.raises(ValueError):
                helios.merged(probe, starttime, endtime)
