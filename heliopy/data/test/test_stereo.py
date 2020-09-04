from datetime import datetime
import pytest

from heliopy.data import stereo
from .util import check_data_output

pytestmark = pytest.mark.data

starttime = datetime(2010, 12, 19)
endtime = datetime(2010, 12, 19, 23)

funs = [stereo.mag_l1_rtn,
        stereo.magplasma_l2,
        stereo.coho1hr_merged,
        stereo.let_l1,
        stereo.sept_l1,
        stereo.sit_l1]


@pytest.mark.parametrize('func', funs)
@pytest.mark.parametrize('sc', ['sta', 'stb', 'a', 'b'])
def test_stereo(func, sc):
    df = func(sc, starttime, endtime)
    check_data_output(df)


@pytest.mark.parametrize('func', funs)
def test_stereo_wrong_identifier(func):
    with pytest.raises(ValueError):
        func('random', starttime, endtime)
