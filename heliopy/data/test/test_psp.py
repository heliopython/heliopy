from datetime import datetime
import pytest

from heliopy.data import psp

from .util import check_data_output

pytest.mark.data()


starttime = datetime(2018, 12, 19)
endtime = datetime(2018, 12, 19, 1)


def test_sweap_spc_l3():
    with pytest.warns(Warning, match='has missing units'):
        df = psp.sweap_spc_l3(starttime, endtime)
    check_data_output(df)


def test_fields_mag_rtn_1min():
    df = psp.fields_mag_rtn_1min(starttime, endtime)
    check_data_output(df)
