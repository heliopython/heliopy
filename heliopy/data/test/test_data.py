import heliopy.data.wind as wind
import heliopy.data.mms as mms
import heliopy.data.helios as helios
import heliopy.data.cluster as cluster
import heliopy.data.ace as ace
import heliopy.data.artemis as artemis
import heliopy.data.imp as imp
import heliopy.data.ulysses as ulysses
import heliopy.data.messenger as messenger
import heliopy.data.cassini as cassini
import heliopy.data.helper as helper
import heliopy.data.spice as spice
import heliopy.data.sunspot as sunspot
import astropy.units as u
from heliopy import config

import pandas as pd
from datetime import datetime
import urllib
import pytest

try:
    from pycdf import pycdf
    no_pycdf = False
except Exception:
    no_pycdf = True


def check_datetime_index(df):
    'Helper funciton to check all dataframes have a datetime index'
    assert type(df.index[0]) == pd.Timestamp


def check_units(df):
    for column in df.data.columns:
        assert type(df.quantity(column)) == u.quantity.Quantity


@pytest.mark.data
class TestSpice:
    def test_built_in(self):
        for kernel in spice.kernel_dict:
            spice.get_kernel(kernel)


@pytest.mark.data
class TestCassini:
    @classmethod
    def setup_class(self):
        self.starttime = datetime(2008, 6, 1, 0, 0, 0)
        self.endtime = datetime(2008, 6, 2, 1, 0, 0)

    def test_mag(self):
        df = cassini.mag_hires(self.starttime, self.endtime)
        check_datetime_index(df)

        # Check that a RTN co-ordinate download works too
        starttime = datetime(2004, 5, 1)
        endtime = datetime(2004, 5, 2)
        df = cassini.mag_hires(starttime, endtime)
        check_datetime_index(df)

        # Check that no data raises an error
        starttime = datetime(2040, 5, 1)
        endtime = datetime(2040, 5, 2)
        with pytest.raises(RuntimeError):
            df = cassini.mag_hires(starttime, endtime)

        df = cassini.mag_1min(self.starttime, self.endtime, 'KSO')
        check_datetime_index(df)


@pytest.mark.skipif(no_pycdf, reason='Importing pycdf failed')
@pytest.mark.data
class TestMessenger:
    @classmethod
    def setup_class(self):
        self.starttime = datetime(2010, 1, 1, 0, 0, 0)
        self.endtime = datetime(2010, 1, 2, 1, 0, 0)

    def test_mag(self):
        df = messenger.mag_rtn(self.starttime, self.endtime)
        check_datetime_index(df)


@pytest.mark.data
class TestUlysses:
    @classmethod
    def setup_class(self):
        self.starttime = datetime(1993, 1, 1, 0, 0, 0)
        self.endtime = datetime(1993, 1, 2, 0, 0, 0)

    def test_fgm_hires(self):
        df = ulysses.fgm_hires(self.starttime, self.endtime)
        check_datetime_index(df)

    def test_swoops_ions(self):
        df = ulysses.swoops_ions(self.starttime, self.endtime)
        check_datetime_index(df.data)
        check_units(df)

    def test_swics_heavy_ions(self):
        df = ulysses.swics_heavy_ions(self.starttime, self.endtime)
        check_datetime_index(df.data)
        check_units(df)

    def test_swics_abundances(self):
        df = ulysses.swics_abundances(self.starttime, self.endtime)
        check_datetime_index(df.data)
        check_units(df)


@pytest.mark.skipif(no_pycdf, reason='Importing pycdf failed')
@pytest.mark.data
class TestArtemis:
    @classmethod
    def setup_class(self):
        self.starttime = datetime(2008, 1, 1, 0, 0, 0)
        self.endtime = datetime(2008, 1, 2, 0, 0, 0)
        self.probe = 'a'

    def test_fgm(self):
        df = artemis.fgm(self.probe, 'h', 'dsl', self.starttime, self.endtime)
        check_datetime_index(df)

        with pytest.raises(ValueError):
            artemis.fgm('123', 'h', 'dsl', self.starttime, self.endtime)
        with pytest.raises(ValueError):
            artemis.fgm('1', '123', 'dsl', self.starttime, self.endtime)
        with pytest.raises(ValueError):
            artemis.fgm('1', 'h', '123', self.starttime, self.endtime)


@pytest.mark.skipif(no_pycdf, reason='Importing pycdf failed')
@pytest.mark.data
class TestAce:
    @classmethod
    def setup_class(self):
        self.starttime = datetime(2010, 1, 1, 0, 0, 0)
        self.endtime = datetime(2010, 1, 2, 0, 0, 0)

    def test_mfi_h0(self):
        df = ace.mfi_h0(self.starttime, self.endtime)
        check_datetime_index(df.data)
        check_units(df)

    def test_swe_h0(self):
        df = ace.swe_h0(self.starttime, self.endtime)
        check_datetime_index(df)

    def test_swi_h2(self):
        df = ace.swi_h2(self.starttime, self.endtime)
        check_datetime_index(df)

    def test_swi_h3(self):
        df = ace.swi_h3(self.starttime, self.endtime)
        check_datetime_index(df)

    def test_swi_h6(self):
        df = ace.swi_h6(self.starttime, self.endtime)
        check_datetime_index(df)


@pytest.mark.skipif(no_pycdf, reason='Importing pycdf failed')
@pytest.mark.data
class TestImp:
    @classmethod
    def setup_class(self):
        self.starttime = datetime(1976, 1, 1, 0, 0, 0)
        self.endtime = datetime(1976, 1, 2, 0, 0, 0)
        self.probe = '8'

    def test_mag320ms(self):
        df = imp.mag320ms(self.probe, self.starttime, self.endtime)
        check_datetime_index(df)

    def test_mag15s(self):
        df = imp.mag15s(self.probe, self.starttime, self.endtime)
        check_datetime_index(df)

    def test_mitplasma_h0(self):
        df = imp.mitplasma_h0(self.probe, self.starttime, self.endtime)
        check_datetime_index(df)

    def test_merged(self):
        df = imp.merged(self.probe, self.starttime, self.endtime)
        check_datetime_index(df)


@pytest.mark.skipif(no_pycdf, reason='Importing pycdf failed')
@pytest.mark.data
@pytest.mark.skipif(config['cluster_cookie'] == 'none',
                    reason='Cluster download cookie not set')
class TestCluster():
    @classmethod
    def setup_class(self):
        self.probe = '3'

    def test_fgm(self):
        starttime = datetime(2004, 6, 18, 11, 35, 0)
        endtime = datetime(2004, 6, 19, 18, 35, 0)
        df = cluster.fgm(self.probe, starttime, endtime)
        check_datetime_index(df)

    def test_peace_moments(self):
        starttime = datetime(2009, 12, 22, 4, 0, 0)
        endtime = datetime(2009, 12, 22, 6)
        df = cluster.peace_moments(self.probe, starttime, endtime)
        check_datetime_index(df)

    def test_cis_hia_onboard_moms(self):
        starttime = datetime(2009, 1, 1, 0, 0, 0)
        endtime = datetime(2009, 1, 1, 2, 0, 0)
        df = cluster.cis_hia_onboard_moms(self.probe, starttime, endtime)
        check_datetime_index(df)

    def test_cis_codif_h1_moms(self):
        starttime = datetime(2009, 1, 1, 0, 0, 0)
        endtime = datetime(2009, 1, 1, 2, 0, 0)
        df = cluster.cis_codif_h1_moms(self.probe, starttime, endtime)
        check_datetime_index(df)


@pytest.mark.skipif(no_pycdf, reason='Importing pycdf failed')
@pytest.mark.data
class TestWind:
    @classmethod
    def setup_class(self):
        self.starttime = datetime(2010, 1, 1, 0, 0, 0)
        self.endtime = datetime(2010, 1, 1, 23, 59, 59)

    def test_mfi_h0(self):
        df = wind.mfi_h0(self.starttime, self.endtime)
        check_datetime_index(df)

    def test_mfi_h2(self):
        df = wind.mfi_h2(self.starttime, self.endtime)
        check_datetime_index(df)

    def test_threedp_pm(self):
        df = wind.threedp_pm(self.starttime, self.endtime)
        check_datetime_index(df)

    def test_threedp_sfpd(self):
        starttime = datetime(2002, 1, 1, 0, 0, 0)
        endtime = datetime(2002, 1, 1, 23, 59, 59)
        df = wind.threedp_sfpd(starttime, endtime)

    def test_swe_h3(self):
        df = wind.swe_h3(self.starttime, self.endtime)

    def test_swe_h1(self):
        df = wind.swe_h1(self.starttime, self.endtime)


@pytest.mark.skipif(no_pycdf, reason='Importing pycdf failed')
@pytest.mark.data
class TestMMS:
    @classmethod
    def setup_class(self):
        self.starttime = datetime(2016, 1, 2, 0, 0, 0)
        self.endtime = datetime(2016, 1, 2, 1, 0, 0)
        self.probe = '1'

    def test_fgm_survey(self):
        df = mms.fgm_survey(self.probe, self.starttime, self.endtime)
        check_datetime_index(df)

    def test_fpi_dis_moms(self):
        df = mms.fpi_dis_moms(self.probe, 'fast', self.starttime, self.endtime)
        check_datetime_index(df)


@pytest.mark.data
class TestHelios:
    @classmethod
    def setup_class(self):
        self.starttime = datetime(1976, 1, 10, 0, 0, 0)
        self.endtime = datetime(1976, 1, 10, 23, 59, 59)
        self.probe = '1'

    def test_merged(self):
        df = helios.merged(self.probe, self.starttime, self.endtime)
        check_datetime_index(df)

        starttime = datetime(2000, 1, 1, 0, 0, 0)
        endtime = datetime(2000, 1, 2, 0, 0, 0)
        with pytest.raises(ValueError):
            helios.merged(self.probe, starttime, endtime)

    def test_corefit(self):
        df = helios.corefit(self.probe, self.starttime, self.endtime)
        check_datetime_index(df)

        starttime = datetime(2000, 1, 1, 0, 0, 0)
        endtime = datetime(2000, 1, 2, 0, 0, 0)
        with pytest.raises(RuntimeError):
            helios.corefit(self.probe, starttime, endtime)

    def test_6sec_ness(self):
        df = helios.mag_ness(self.probe, self.starttime, self.endtime)
        check_datetime_index(df)

    def test_mag_4hz(self):
        df = helios.mag_4hz(self.probe, self.starttime, self.endtime)
        check_datetime_index(df)


class TestHelper:
    def test_listdata(self):
        helper.listdata()


@pytest.mark.data
class TestSunspot:

    def test_daily(self):
        assert len(sunspot.daily().columns) == 8

    def test_monthly(self):
        assert len(sunspot.monthly().columns) == 7

    def test_yearly(self):
        assert len(sunspot.yearly().columns) == 5
