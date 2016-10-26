from pyspace.time import *
import pytest


def test_doy2ymd():
    assert doy2ymd(2015, 3) == (2015, 1, 3)
    assert doy2ymd(2016, 32) == (2016, 2, 1)
    with pytest.raises(ValueError):
        doy2ymd(2014, 366)
    with pytest.raises(ValueError):
        doy2ymd(2012, 367)
