from datetime import datetime
import pytest

from .util import check_data_output

artemis = pytest.importorskip('heliopy.data.artemis')
pytest.mark.data()

starttime = datetime(2008, 1, 1)
endtime = datetime(2008, 1, 2)
probe = 'a'


def test_fgm():
    with pytest.warns(UserWarning,
                      match='Discarding nonzero nanoseconds in conversion'):
        df = artemis.fgm(probe, 'l', 'dsl', starttime, endtime)
    check_data_output(df)

    with pytest.raises(ValueError):
        artemis.fgm('123', 'h', 'dsl', starttime, endtime)
    with pytest.raises(ValueError):
        artemis.fgm('1', '123', 'dsl', starttime, endtime)
    with pytest.raises(ValueError):
        artemis.fgm('1', 'h', '123', starttime, endtime)
