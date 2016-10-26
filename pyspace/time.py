'''
Methods for processing times and dates
'''


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
    assert isinstance(y, int) and isinstance(doy, int), 'Input year and day of year must be integers'
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
            raise ValueError('Day of year cannot be greater than 365 in a non leap yaer')
        days = nonleap

    for i in range(len(days)):
        if days[i] < doy:
            doy -= days[i]
        else:
            m = i + 1
            d = doy
            break

    return y, m, d
