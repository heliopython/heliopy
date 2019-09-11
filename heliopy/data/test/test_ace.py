from datetime import datetime
import pytest

from .util import check_data_output

ace = pytest.importorskip('heliopy.data.ace')
pytest.mark.data()

starttime = datetime(2018, 1, 1, 0, 0, 0)
endtime = datetime(2019, 1, 1, 0, 0, 0)


def test_mfi_h0():
    df = ace.mfi_h0(starttime, endtime)
    check_data_output(df)


def test_swi_h3b():
    df = ace.swi_h3b(datetime(2013, 1, 1), datetime(2013, 1, 1, 12))
    check_data_output(df)


# No data currently available?
'''
def test_swi_h4():
    df = ace.swi_h4(starttime, endtime + timedelta(days=2))
    check_data_output(df)
'''


def test_swi_h5():
    df = ace.swi_h5(starttime, endtime)
    check_data_output(df)


def test_mfi_h1():
    df = ace.mfi_h1(starttime, endtime)
    check_data_output(df)


def test_mfi_h2():
    df = ace.mfi_h2(starttime, endtime)
    check_data_output(df)


def test_mfi_h3():
    df = ace.mfi_h3(starttime, endtime)
    check_data_output(df)


def test_swe_h0():
    df = ace.swe_h0(starttime, endtime)
    check_data_output(df)


def test_swe_h2():
    df = ace.swe_h2(starttime, endtime)
    check_data_output(df)


def test_swi_h2():
    df = ace.swi_h2(starttime, endtime)
    check_data_output(df)


def test_swi_h3():
    df = ace.swi_h3(starttime, endtime)
    check_data_output(df)


def test_swi_h6():
    df = ace.swi_h6(starttime, endtime)
    check_data_output(df)
