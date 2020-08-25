from datetime import datetime
import pytest

from heliopy.data import stereo
from .util import check_data_output

pytestmark = pytest.mark.data

starttime = datetime(2010, 12, 19)
endtime = datetime(2010, 12, 20)


@pytest.mark.parametrize('func', [stereo.mag_l1_rtn,
                                  stereo.magplasma_l2])
@pytest.mark.parametrize('sc', ['sta', 'stb'])
def test_psp(func, sc):
    df = func(sc, starttime, endtime)
    check_data_output(df)

    with pytest.raises(ValueError):
        func('random', starttime, endtime)
