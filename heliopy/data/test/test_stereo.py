from datetime import datetime
import pytest

from heliopy.data import stereo
from .util import check_data_output

pytestmark = pytest.mark.data

starttime = datetime(2010, 12, 19)
endtime = datetime(2010, 12, 20)


@pytest.mark.parametrize('func', [stereo.coho1hr_merged])
@pytest.mark.parametrize('sc', ['A', 'B'])
def test_psp(func, sc):
    df = func(sc, starttime, endtime)
    check_data_output(df)

    with pytest.raises(ValueError):
        func('random', starttime, endtime)
