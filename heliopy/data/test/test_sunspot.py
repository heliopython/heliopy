import pytest

import heliopy.data.sunspot as sunspot

pytestmark = pytest.mark.data


def test_daily():
    assert len(sunspot.daily().columns) == 8


def test_monthly():
    assert len(sunspot.monthly().columns) == 7


def test_yearly():
    assert len(sunspot.yearly().columns) == 5
