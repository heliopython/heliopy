from datetime import datetime
import pytest

from heliopy.data import psp

from .util import check_data_output

pytestmark = pytest.mark.data

starttime = datetime(2018, 12, 19)
endtime = datetime(2018, 12, 19, 1)


@pytest.mark.parametrize('func', [psp.sweap_spc_l2,
                                  psp.sweap_spc_l3,
                                  psp.fields_mag_rtn_1min,
                                  psp.fields_mag_rtn_4_per_cycle,
                                  psp.fields_mag_rtn])
def test_psp(func):
    df = func(starttime, endtime)
    check_data_output(df)
