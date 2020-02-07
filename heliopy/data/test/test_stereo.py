from datetime import datetime
import pytest

from .util import check_data_output

stereo = pytest.importorskip('heliopy.data.stereo')
pytest.mark.data()

starttime = datetime(2010, 1, 1, 0, 0, 0)
endtime = datetime(2010, 1, 2, 0, 0, 0)

def test_mag_l1_rtn():
    df = stereo.mag_l1_rtn(starttime, endtime)
    check_data_output(df)


def test_magplasma_l2():
    df = stereo.magplasma_l2(starttime, endtime)
    check_data_output(df)


def test_let_l1():
    df = stereo.let_l1(starttime, endtime)
    check_data_output(df)


def test_sept_l1():
    df = stereo.sept_l1(starttime, endtime)
    check_data_output(df)


def test_sit_l1():
    df = stereo.sit_l1(starttime, endtime)
    check_data_output(df)


def test_ste_l1():
    df = stereo.ste_l1(starttime, endtime)
    check_data_output(df)


def test_het_l1():
    df = stereo.het_l1(starttime, endtime)
    check_data_output(df)
