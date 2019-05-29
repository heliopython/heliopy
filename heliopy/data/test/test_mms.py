from datetime import datetime
import pytest

from .util import check_data_output

mms = pytest.importorskip('heliopy.data.mms')
pytest.mark.data()


starttime = datetime(2016, 1, 2, 0, 0, 0)
endtime = datetime(2016, 1, 2, 1, 0, 0)
probe = '1'


def test_fgm():
    df = mms.fgm(probe, 'srvy', starttime, endtime)
    check_data_output(df)


def test_fpi_dis_moms():
    df = mms.fpi_dis_moms(probe, 'fast', starttime, endtime)
    check_data_output(df)


def test_fpi_des_moms():
    df = mms.fpi_des_moms(probe, 'fast', starttime, endtime)
    check_data_output(df)


def test_fpi_dis_dist():
    df = mms.fpi_dis_dist(probe, 'fast', starttime, endtime)
    check_data_output(df)


def test_fpi_des_dist():
    df = mms.fpi_des_dist(probe, 'fast', starttime, endtime)
    check_data_output(df)
