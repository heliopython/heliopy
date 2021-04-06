from datetime import datetime

import pytest

from .util import check_data_output

mms = pytest.importorskip('heliopy.data.mms')
pytestmark = pytest.mark.data


starttime = datetime(2016, 1, 2, 0, 0, 0)
endtime = datetime(2016, 1, 2, 1, 0, 0)
probes = ['1', '4']


@pytest.mark.skip()
@pytest.mark.parametrize("probe", probes)
def test_fgm(probe):
    df = mms.fgm(probe, 'srvy', starttime, endtime)
    check_data_output(df)


@pytest.mark.parametrize("probe", probes)
def test_fpi_dis_moms(probe):
    df = mms.fpi_dis_moms(probe, 'fast', starttime, endtime)
    check_data_output(df)


@pytest.mark.parametrize("probe", probes)
def test_fpi_des_moms(probe):
    df = mms.fpi_des_moms(probe, 'fast', starttime, endtime)
    check_data_output(df)


# These tests take a *long* time to run, so comment them out
@pytest.mark.skip()
@pytest.mark.parametrize("probe", probes)
def test_fpi_dis_dist(probe):
    df = mms.fpi_dis_dist(probe, 'fast', starttime, endtime)
    check_data_output(df)


@pytest.mark.skip()
@pytest.mark.parametrize("probe", probes)
def test_fpi_des_dist(probe):
    df = mms.fpi_des_dist(probe, 'fast', starttime, endtime)
    check_data_output(df)


def test_narrow_interval():
    # Check that a narrow time interval downloads properly
    starttime = datetime(2017, 7, 11, 22, 30)
    endtime = datetime(2017, 7, 11, 22, 36)

    data = mms.fpi_dis_moms(1, 'fast', starttime, endtime)
    check_data_output(data)
