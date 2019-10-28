from datetime import datetime
import pytest

from .util import check_data_output

wind = pytest.importorskip('heliopy.data.wind')
pytest.mark.data()

starttime = datetime(2010, 1, 1, 0, 0, 0)
endtime = datetime(2010, 1, 1, 23, 59, 59)


def test_mfi_h0():
    df = wind.mfi_h0(starttime, endtime)
    check_data_output(df)


def test_mfi_h2():
    df = wind.mfi_h2(starttime, endtime)
    check_data_output(df)


def test_threedp_pm():
    df = wind.threedp_pm(starttime, endtime)
    check_data_output(df)


def test_threedp_e0_emfits():
    df = wind.threedp_pm(starttime, endtime)
    check_data_output(df)


def test_swe_h1():
    df = wind.swe_h1(starttime, endtime)
    check_data_output(df)


def test_swe_h3():
    df = wind.swe_h3(starttime, endtime)
    check_data_output(df)
