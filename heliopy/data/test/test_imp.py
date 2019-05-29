import os
from datetime import datetime
import pytest

from .util import check_data_output

imp = pytest.importorskip('heliopy.data.imp')
pytest.mark.data()

starttime = datetime(1976, 1, 1, 0, 0, 0)
endtime = datetime(1976, 1, 2, 0, 0, 0)
probe = '8'


def test_mag320ms():
    df = imp.i8_mag320ms(starttime, endtime)
    check_data_output(df)


def test_mag15s():
    df = imp.i8_mag15s(starttime, endtime)
    check_data_output(df)


def test_mitplasma_h0():
    df = imp.i8_mitplasma(starttime, endtime)
    check_data_output(df)


@pytest.mark.skipif('TRAVIS' in os.environ,
                    reason='Needs FTP capabilities')
def test_merged():
    df = imp.merged(probe, starttime, endtime)
    check_data_output(df)
