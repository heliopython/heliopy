from datetime import datetime, time, timedelta
'''
Methods for processing times and dates
'''


def daysplitinterval(startTime, endTime):
    '''
    Splits an interval into a list of dates, start times and end times
    '''
    assert startTime < endTime, 'Start datetime must be before end datetime'
    out = []
    return daysplitintervalhelper(startTime, endTime, out)


def daysplitintervalhelper(startTime, endTime, out):
    # If two datetimes are on the same day, append current date and
    # start/end times
    if startTime.date() == endTime.date():
        out.append([startTime.date(), startTime.time(), endTime.time()])
        return out

    # Append current date, start time, and maximum time
    out.append([startTime.date(), startTime.time(), time.max])
    # Set new start time to 00:00 on the next day
    newstartTime = datetime.combine(startTime.date(), time.min) +\
        timedelta(days=1)
    # Recurse
    return daysplitintervalhelper(newstartTime, endTime, out)


def isLeap(y):
    '''
    Returns true if year is a leap year, false otherwise
    '''
    rem1 = (y % 4) == 0
    rem2 = (y % 100) == 0
    rem3 = (y % 400) == 0
    return (rem1 != rem2) or rem3


def doy2ymd(y, doy):
    '''
    Converts day of year and year to year, month, day
    '''
    assert isinstance(y, int) and isinstance(doy, int),\
        'Input year and day of year must be integers'
    # Days in each month
    nonleap = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    leap = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # Select the right days
    if isLeap(y):
        if doy > 366:
            raise ValueError('Day of year cannot be greater than 366')
        days = leap
    else:
        if doy > 365:
            raise ValueError('Day of year cannot be greater than 365\
                             in a non leap year')
        days = nonleap

    for i in range(len(days)):
        if days[i] < doy:
            doy -= days[i]
        else:
            m = i + 1
            d = doy
            break

    return y, m, d
