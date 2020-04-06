from datetime import datetime
import pytest

from .util import check_data_output
import heliopy.data.ulysses as ulysses

pytestmark = pytest.mark.data

starttime = datetime(1990, 12, 30)
endtime = datetime(1991, 1, 1)


def test_fgm_hires():
    df = ulysses.fgm_hires(starttime, endtime)
    check_data_output(df)


def test_swoops_ions():
    df = ulysses.swoops_ions(starttime, endtime)
    check_data_output(df)


def test_swics_heavy_ions():
    df = ulysses.swics_heavy_ions(starttime, endtime)
    check_data_output(df)


def test_swics_abundances():
    df = ulysses.swics_abundances(starttime, endtime)
    check_data_output(df)
