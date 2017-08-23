"""Methods for processing times and dates"""
from datetime import datetime, time, date, timedelta
import numpy as np
import pandas as pd


def daysplitinterval(starttime, endtime):
    """
    Splits an interval into a list of dates, start times and end times

    Parameters
    ----------
    starttime : datetime
        Start date/time of interval
    endtime : datetime
        End date/time of interval

    Returns
    -------
    intervals : list
        A list of lists. Each item in the sublists consists of the date,
        start time, and end time for the particular date.
    """
    assert starttime < endtime, 'Start datetime must be before end datetime'
    out = []
    return _daysplitintervalhelper(starttime, endtime, out)


def _daysplitintervalhelper(starttime, endtime, out):
    # If two datetimes are on the same day, append current date and
    # start/end times
    if starttime.date() == endtime.date():
        out.append([starttime.date(), starttime.time(), endtime.time()])
        return out

    # Append current date, start time, and maximum time
    out.append([starttime.date(), starttime.time(), time.max])
    # Set new start time to 00:00 on the next day
    newstarttime = datetime.combine(starttime.date(), time.min) +\
        timedelta(days=1)
    # Recurse
    return _daysplitintervalhelper(newstarttime, endtime, out)


def isleap(y):
    """
    Returns true if year is a leap year, false otherwise.

    Parameters
    ----------
    y : int
        Year

    Returns
    -------
    leap : bool
        True if y is a leap year, false otherwise
    """
    rem1 = (y % 4) == 0
    rem2 = (y % 100) == 0
    rem3 = (y % 400) == 0
    return (rem1 != rem2) or rem3


def doy2ymd(y, doy):
    """
    Converts day of year and year to year, month, day

    Parameters
    ----------
        y : int
            Year.
        doy : int
            Day of year.

    Returns
    -------
    year : int
        Year
    month : int
        Month
    day : int
        Day of month
    """
    d = datetime.strptime(str(y) + ':' + str(doy), '%Y:%j')

    return d.year, d.month, d.day


def dtime2doy(dt):
    """
    Returns day of year of a datetime object.

    Parameters
    ----------
    dt : datetime

    Returns
    -------
    doy : int
        Day of year
    """
    return int(dt.strftime('%j'))
