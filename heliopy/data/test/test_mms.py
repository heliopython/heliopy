from datetime import datetime
import pytest

from .util import check_data_output


mms = pytest.importorskip('heliopy.data.mms')
pytest.mark.data()


#starttime = datetime(2016, 1, 2, 0, 0, 0)
#endtime = datetime(2016, 1, 2, 1, 0, 0)
#probes = ['1', '4']



starttime = datetime(2018, 4, 8, 0, 0, 0)
endtime = datetime(2018, 4, 8, 1, 0, 0)
probes = ['1']


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


@pytest.mark.parametrize("probe", probes)
def test_fpi_dis_dist(probe):
    df = mms.fpi_dis_dist(probe, 'fast', starttime, endtime)
    check_data_output(df)


@pytest.mark.parametrize("probe", probes)
def test_fpi_des_dist(probe):
    df = mms.fpi_des_dist(probe, 'fast', starttime, endtime)
    check_data_output(df)
