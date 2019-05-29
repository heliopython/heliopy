import heliopy.data.sunspot as sunspot


def test_daily(self):
    assert len(sunspot.daily().columns) == 8


def test_monthly(self):
    assert len(sunspot.monthly().columns) == 7


def test_yearly(self):
    assert len(sunspot.yearly().columns) == 5
