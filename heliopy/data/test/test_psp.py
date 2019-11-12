from datetime import datetime
import pytest

from heliopy.data import psp

from .util import check_data_output

pytest.mark.data()


starttime = datetime(2018, 10, 25)
endtime = datetime(2018, 10, 25, 1)


def test_sweap_spc_l3():
    df = psp.sweap_spc_l3(starttime, endtime)
    check_data_output(df)
