from heliopy.time import *
from datetime import datetime, time, date
import pytest
import numpy as np


def test_daysplitinterval():
    startTime = datetime(1992, 12, 20, 4, 5, 6)
    endTime = datetime(1992, 12, 22, 3, 5, 7)
    out = daysplitinterval(startTime, endTime)
    expected = [[date(1992, 12, 20), time(4, 5, 6), time.max],
                [date(1992, 12, 21), time.min, time.max],
                [date(1992, 12, 22), time.min, time(3, 5, 7)]]
    assert out == expected

    startTime = datetime(1992, 12, 21, 4, 5, 6)
    endTime = datetime(1992, 12, 21, 5, 6, 7)
    print(startTime, endTime)
    out = daysplitinterval(startTime, endTime)
    print(out)
    expected = [[date(1992, 12, 21), time(4, 5, 6), time(5, 6, 7)]]
    assert out == expected


def test_doy2ymd():
    assert doy2ymd(2015, 3) == (2015, 1, 3)
    assert doy2ymd(2016, 32) == (2016, 2, 1)
