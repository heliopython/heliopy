from datetime import datetime

from heliopy.data import util


def test_monthly_intervals():
    intervals = util.Downloader.intervals_monthly(
        datetime(1992, 11, 1), datetime(1992, 12, 1))
    assert len(intervals) == 2

    intervals = util.Downloader.intervals_monthly(
        datetime(1992, 11, 1), datetime(1992, 11, 10))
    assert len(intervals) == 1


def test_yearly_intervals():
    intervals = util.Downloader.intervals_yearly(
        datetime(1992, 11, 1), datetime(1993, 2, 1))
    assert len(intervals) == 2
