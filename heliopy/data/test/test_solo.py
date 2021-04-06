from datetime import datetime

import pytest

from heliopy.data import solo

from .util import check_data_output

pytestmark = pytest.mark.data

starttime = datetime(2020, 8, 1)
endtime = datetime(2020, 8, 2)


@pytest.mark.parametrize('descriptor', (['MAG']))
def test_solo_ll(descriptor):
    with pytest.warns(
            UserWarning,
            match='Low latency data is not suitable for publication'):
        df = solo.download(starttime, endtime, descriptor, 'LL02')
    check_data_output(df)


@pytest.mark.parametrize('descriptor', (['MAG-RTN-NORMAL',
                                         'SWA-PAS-GRND-MOM']))
def test_solo_science(descriptor):
    starttime = datetime(2020, 9, 1)
    endtime = datetime(2020, 9, 1, 12)
    df = solo.download(starttime, endtime, descriptor, 'L2')
    check_data_output(df)


def test_solo_bad_descriptor():
    with pytest.raises(
            RuntimeError, match='No data files found for descriptor=GARBAGE'):
        df = solo.download(starttime, endtime, 'garbage', 'LL02')
