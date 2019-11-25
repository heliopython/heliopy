from datetime import datetime
import pytest

from .util import check_data_output_ts
from .util import check_data_output_xr

mms = pytest.importorskip('heliopy.data.mms')
pytest.mark.data()


starttime = datetime(2016, 1, 2, 0, 0, 0)
endtime = datetime(2016, 1, 2, 1, 0, 0)
probes = ['1', '4']


# Test SunPy TimeSeries as outputs
@pytest.mark.parametrize("probe", probes)
def test_fgm_ts(probe):
    data = mms.fgm(probe, 'srvy', starttime, endtime)
    check_data_output_ts(data)


@pytest.mark.parametrize("probe", probes)
def test_fpi_dis_moms_ts(probe):
    data = mms.fpi_dis_moms(probe, 'fast', starttime, endtime)
    check_data_output_ts(data)


@pytest.mark.parametrize("probe", probes)
def test_fpi_des_moms_ts(probe):
    data = mms.fpi_des_moms(probe, 'fast', starttime, endtime)
    check_data_output_ts(data)


@pytest.mark.parametrize("probe", probes)
def test_fpi_dis_dist_ts(probe):
    data = mms.fpi_dis_dist(probe, 'fast', starttime, endtime)
    check_data_output_ts(data)


@pytest.mark.parametrize("probe", probes)
def test_fpi_des_dist_ts(probe):
    data = mms.fpi_des_dist(probe, 'fast', starttime, endtime)
    check_data_output_ts(data)


def test_narrow_interval():
    # Check that a narrow time interval downloads properly
    starttime = datetime(2017, 7, 11, 22, 30)
    endtime = datetime(2017, 7, 11, 22, 36)

    data = mms.fpi_dis_moms(1, 'fast', starttime, endtime)
    check_data_output(data)


# Test xarrays as outputs
@pytest.mark.parametrize("probe", probes)
def test_fgm_xr(probe):
    data = mms.fgm(probe, 'srvy', starttime, endtime, want_xr=True)
    check_data_output_xr(data)


@pytest.mark.parametrize("probe", probes)
def test_fpi_dis_moms_xr(probe):
    data = mms.fpi_dis_moms(probe, 'fast', starttime, endtime, want_xr=True)
    check_data_output_xr(data)


@pytest.mark.parametrize("probe", probes)
def test_fpi_des_moms_xr(probe):
    data = mms.fpi_des_moms(probe, 'fast', starttime, endtime, want_xr=True)
    check_data_output_xr(data)


@pytest.mark.parametrize("probe", probes)
def test_fpi_dis_dist_xr(probe):
    data = mms.fpi_dis_dist(probe, 'fast', starttime, endtime, want_xr=True)
    check_data_output_xr(data)


@pytest.mark.parametrize("probe", probes)
def test_fpi_des_dist_xr(probe):
    data = mms.fpi_des_dist(probe, 'fast', starttime, endtime, want_xr=True)
    check_data_output_xr(data)
