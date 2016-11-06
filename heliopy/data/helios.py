"""Methods for importing Helios data."""
import pandas as pd
import numpy as np
import datetime
import os
import warnings

from heliopy import config
import heliopy.vector.transformations as spacetrans
import heliopy.time as spacetime
import heliopy.constants as constants
data_dir = config['default']['download_dir']
helios_dir = data_dir + '/helios'


####################################################
# Consistent method to convert datetime to ordinal #
####################################################
def dtime2ordinal(dtime):
    if type(dtime) == datetime.datetime:
        dtime = pd.Series(dtime)
    return pd.DatetimeIndex(dtime).astype(np.int64)


def loaddistfile(probe, year, doy, hour, minute, second):
    """
    Method to load a Helios distribution file.

    Returns opened file and location of file if file exists. If file doesn't
    exist raises an OSError.

    Parameters
    ----------
        probe : int
            Helios probe to import data from. Must be 1 or 2.
        year : int
            Year
        doy : int
            Day of year.
        hour : int
            Hour.
        minute : int
            Minute.
        second : int
            Second.
    """
    assert probe == '1' or probe == '2', 'Probe must be 1 or 2'
    # Work out location of file
    yearstring = str(year)[-2:]
    filename = helios_dir + '/helios' + probe + '/dist/h' + probe + yearstring +\
        '/Y' + yearstring + 'D' + str(doy).zfill(3) + \
        '/h' + probe + 'y' + yearstring + 'd' + str(doy).zfill(3) + \
        'h' + str(hour).zfill(2) + 'm' + str(minute).zfill(2) + 's' +\
        str(second).zfill(2) + '_'

    # Try to open distribution file
    for extension in ['hdm.0', 'hdm.1', 'ndm.0', 'ndm.1']:
        try:
            f = open(filename + extension)
            filename += extension
        except OSError:
            continue

    if 'f' not in locals():
        raise OSError('Could not find file with name ' +
                                filename[:-1])
    else:
        return f, filename


def integrateddists(probe, year, doy, hour, minute, second):
    """
    Returns the integrated distributions from experiments i1a and i1b in Helios
    distribution function files.
    """
    f, _ = loaddistfile(probe, year, doy, hour, minute, second)
    for line in f:
        if line[0:19] == ' 1-D i1a integrated':
            break
    # i1a distribution function
    i1adf = f.readline().split()
    f.readline()
    i1avs = f.readline().split()
    f.readline()
    # i1b distribution file
    i1bdf = f.readline().split()
    f.readline()
    i1bvs = f.readline().split()

    i1a = pd.DataFrame({'v': i1avs, 'df': i1adf}, dtype=float)
    i1b = pd.DataFrame({'v': i1bvs, 'df': i1bdf}, dtype=float)
    return i1a, i1b


def distribution(probe, year, doy, hour, minute, second):
    """Read in full distribution functions and associated paraemters."""
    f, filename = loaddistfile(probe, year, doy, hour, minute, second)

    _, month, day = spacetime.doy2ymd(year, doy)
    dtime = datetime.datetime(year, month, day, hour, minute, second)
    distparams = pd.Series(dtime, index=['Time'], dtype=object)
    # Ignore the Pizzo et. al. correction at top of file
    for i in range(0, 3):
        f.readline()
    # Line of flags
    flags = f.readline().split()
    distparams['imode'] = int(flags[0])
    distparams['ishift'] = bool(flags[1])     # Alternating energy/azimuth shift on?
    distparams['iperihelion_shift'] = bool(flags[2])    # Possibly H2 abberation shift?
    distparams['minus'] = int(flags[3])  # Indicates a HDM file which contained bad data (frames), but could be handled as NDM file
    distparams['ion_instrument'] = int(flags[4])  # 0 = no instrument, 1 = i1a, 2 = I3

    # 2 lines of Helios location information
    location = f.readline().split()
    distparams['r_sun'] = float(location[0])     # Heliospheric distance (AU)
    distparams['clong'] = float(location[1])    # Carrington longitude (deg)
    distparams['clat'] = float(location[2])     # Carrington lattitude (deg)
    distparams['carrot'] = int(f.readline().split()[0])   # Carrington cycle

    # 2 lines of Earth location information
    earth_loc = f.readline().split()
    distparams['earth_rsun'] = float(earth_loc[0])     # Heliospheric distance (AU)
    distparams['earth_clong'] = float(earth_loc[1])    # Carrington longitude (deg)
    distparams['earth_clat'] = float(earth_loc[2])     # Carrington lattitude (deg)
    earth_loc = f.readline().split()
    distparams['earth_he_angle'] = float(earth_loc[0])    # Angle between Earth and Helios (deg)
    distparams['earth_carrot'] = int(earth_loc[1])        # Carrington rotation

    # Helios velocity information
    helios_v = f.readline().split()
    distparams['helios_vr'] = float(helios_v[0]) * 1731  # Helios radial velocity (km/s)
    distparams['helios_v'] = float(helios_v[1]) * 1731   # Helios tangential velocity (km/s)

    # i1a integrated ion parameters
    i1a_proton_params = f.readline().split()
    distparams['np_i1a'] = float(i1a_proton_params[0])   # Proton number density (cm^-3)
    distparams['vp_i1a'] = float(i1a_proton_params[1])   # Proton velocity (km/s)
    distparams['Tp_i1a'] = float(i1a_proton_params[2])   # Proton temperature (K)
    i1a_proton_params = f.readline().split()
    distparams['v_az_i1a'] = float(i1a_proton_params[0])     # Proton azimuth flow angle (deg)
    distparams['v_el_i1a'] = float(i1a_proton_params[1])     # Proton elevation flow angle (deg)
    assert distparams['v_az_i1a'] < 360, 'Flow azimuth must be less than 360 degrees'

    # i1a integrated alpha parameters (possibly all zero?)
    i1a_alpha_params = f.readline().split()
    distparams['na_i1a'] = float(i1a_alpha_params[0])     # Alpha number density (cm^-3)
    distparams['va_i1a'] = float(i1a_alpha_params[1])     # Alpha velocity (km/s)
    distparams['Ta_i1a'] = float(i1a_alpha_params[2])     # Alpha temperature (K)

    # i1b integrated ion parameters
    i1b_proton_params = f.readline().split()
    distparams['np_i1b'] = float(i1b_proton_params[0])   # Proton number density (cm^-3)
    distparams['vp_i1b'] = float(i1b_proton_params[1])   # Proton velocity (km/s)
    distparams['Tp_i1b'] = float(i1b_proton_params[2])   # Proton temperature (K)

    # Magnetic field (out by a factor of 10 in data files for some reason)
    B = f.readline().split()
    distparams['Bx'] = float(B[0]) / 10
    distparams['By'] = float(B[1]) / 10
    distparams['Bz'] = float(B[2]) / 10
    sigmaB = f.readline().split()
    distparams['sigmaBx'] = float(sigmaB[0]) / 10
    distparams['sigmaBy'] = float(sigmaB[1]) / 10
    distparams['sigmaBz'] = float(sigmaB[2]) / 10

    # Replace bad values with nans
    to_replace = {'Tp_i1a': [-1.0, 0], 'np_i1a': [-1.0, 0], 'vp_i1a': [-1.0, 0],
                  'Tp_i1b': [-1.0, 0], 'np_i1b': [-1.0, 0], 'vp_i1b': [-1.0, 0],
                  'sigmaBx': -0.01, 'sigmaBy': -0.01, 'sigmaBz': -0.01,
                  'Bx': 0.0, 'By': 0.0, 'Bz': 0.0,
                  'v_az_i1a': [-1, 0], 'v_el_i1a': [-1, 0],
                  'na_i1a': [-1, 0], 'va_i1a': [-1, 0], 'Ta_i1a': [-1, 0]}
    distparams = distparams.replace(to_replace, np.nan)

    nionlines = None   # Stores number of lines in ion distribution function
    electronstartline = None    # Stores number of lines in electron distribution function
    linesread = 16  # Stores the total number of lines read in the file
    # Loop through file to find end of ion distribution function
    for i, line in enumerate(f):
        # Find start of proton distribution function
        if line[0:23] == 'Maximum of distribution':
            ionstartline = i + linesread
        # Find number of lines in ion distribution function
        if line[0:4] == ' 2-D':
            electronstartline = i + linesread + 1
            nionlines = i - ionstartline
            break

    linesread += i
    # Bizzare case where there are two proton distributions in one file,
    # or there's no electron data available
    for i, line in enumerate(f):
        if line[0:27] == ' no electron data available':
            electronstartline = None
        if line[0:23] == 'Maximum of distribution' or\
           line[0:30] == '  1.2 Degree, Pizzo correction' or\
           line[0:30] == ' -1.2 Degree, Pizzo correction':
            warnings.warn("More than one ion distribution function found",
                          RuntimeWarning)
            # NOTE: Bodge
            linesread -= 1
            break

    # Get number of lines in electron distribution function
    if electronstartline is None:
        nelectronlines = 0
    else:
        nelectronlines = i - electronstartline + linesread + 1
    f.close()

    # If there's no electron data to get number of lines, set end of ion
    # distribution function to end of file
    if nionlines is None:
        nionlines = i - ionstartline + 1

    #####################################
    # Read and process ion distribution #
    #####################################
    # If no ion data in file
    if nionlines < 1:
        iondist = None
    else:
        # Arguments for reading in data
        readargs = {'usecols': [0, 1, 2, 3, 4, 5, 6, 7],
                    'names': ['Az', 'El', 'E_bin', 'pdf', 'counts',
                              'vx', 'vy', 'vz'],
                    'delim_whitespace': True,
                    'skiprows': ionstartline,
                    'nrows': nionlines}
        # Read in data
        iondist = pd.read_table(filename, **readargs)

        # Work out when maximum of distribution was recorded
        maxbin = np.argmax(iondist['pdf'])
        distparams['Peak Time'] = iondist.loc[maxbin, 'E_bin']

        # Remove spacecraft abberation
        # Assumes that spacecraft motion is always in the ecliptic (x-y) plane
        iondist['vx'] += distparams['helios_vr']
        iondist['vy'] += distparams['helios_v']
        # Convert to SI units
        iondist[['vx', 'vy', 'vz']] *= 1e3
        iondist['pdf'] *= 1e12
        # Calculate magnitude, elevation and azimuth of energy bins
        iondist['|v|'], iondist['theta'], iondist['phi'] =\
            spacetrans.cart2sph(iondist['vx'], iondist['vy'], iondist['vz'])
        # Calculate bin energy assuming particles are protons
        iondist['E_proton'] = 0.5 * constants.m_p * ((iondist['|v|']) ** 2)

    ##########################################
    # Read and process electron distribution #
    ##########################################
    # If no electron data in file
    if nelectronlines < 1:
        electrondist = None
    else:
        # Arguments for reading in data
        readargs = {'usecols': [0, 1, 2, 3, 4, 5],
                    'names': ['Az', 'E_bin', 'pdf', 'counts', 'vx', 'vy'],
                    'delim_whitespace': True,
                    'skiprows': electronstartline,
                    'nrows': nelectronlines}
        # Read in data
        electrondist = pd.read_table(filename, **readargs)

        # Remove spacecraft abberation
        # Assumes that spacecraft motion is always in the ecliptic (x-y) plane
        electrondist['vx'] += distparams['helios_vr']
        electrondist['vy'] += distparams['helios_v']
        # Convert to SI units
        electrondist[['vx', 'vy']] *= 1e3
        electrondist['pdf'] *= 1e12
        # Calculate spherical coordinates of energy bins
        electrondist['|v|'], _, electrondist['phi'] =\
            spacetrans.cart2sph(electrondist['vx'], electrondist['vy'], 0)
        # Calculate bin energy assuming particles are electrons
        electrondist['E_electron'] = 0.5 * constants.m_e *\
            ((electrondist['|v|']) ** 2)

    return electrondist, iondist, distparams


def merged(probe, starttime, endtime, verbose=True):
    """
    Read in merged data set

    starttime and endtime can either be datetime.date or datetime.datetime
    If they are datetime.date, load whole days inclusive of dates given
    """
    if isinstance(starttime, datetime.datetime):
        assert isinstance(endtime, datetime.datetime),\
            'Start time and end time must have same datatype'
        startdate = starttime.date()
        enddate = endtime.date()
    elif isinstance(starttime, datetime.date):
        assert isinstance(endtime, datetime.date),\
            'Start time and end time must have same datatype'
        startdate = starttime
        enddate = endtime

    data = []
    # Loop through years
    for year in range(startdate.year, enddate.year + 1):
        floc = helios_dir + '/helios' + probe + '/merged/he' + probe + '_40sec/'
        # Calculate start day
        startdoy = 1
        if year == startdate.year:
            startdoy = int(startdate.strftime('%j'))

        # Calculate end day
        enddoy = 366
        if year == enddate.year:
            enddoy = int(enddate.strftime('%j'))

        # Loop through days of year
        for doy in range(startdoy, enddoy + 1):
            hdfloc = floc + 'H' + probe + str(year - 1900) + '_' +\
                str(doy).zfill(3) + '.h5'
            if not os.path.isfile(hdfloc):
                # Data not processed yet, try to process and load it
                try:
                    data.append(merged_fromascii(probe, year, doy))
                    if verbose:
                        print(year, doy, 'Processed ascii file')
                except ValueError as err:
                    if verbose:
                        print(str(err))
                        print(year, doy, 'No raw merged data')
            else:
                # Load data from already processed file
                data.append(pd.read_hdf(hdfloc, 'table'))
                if verbose:
                    print(year, doy)

    if data == []:
        fmt = '%d-%m-%Y'
        raise ValueError('No data to import for probe ' + probe +
                         ' between ' + startdate.strftime(fmt) + ' and ' +
                         enddate.strftime(fmt))

    data = pd.concat(data, ignore_index=True)
    # If given datetimes, filter data
    if isinstance(starttime, datetime.datetime):
        data = data[(data['Time'] > starttime) & (data['Time'] < endtime)]

    return data


def merged_fromascii(probe, year, doy):
    """Read in a single day of merged data."""
    floc = helios_dir + '/helios' + probe + '/merged/he' + probe + '_40sec/'
    fname = 'H' + probe + str(year - 1900) + '_' + str(doy).zfill(3)
    asciiloc = floc + fname + '.dat'
    if not os.path.isfile(asciiloc):
        raise ValueError('No raw merged data available for probe ' + probe +
                         ', Year: ' + str(year) + ' DOY: ' + str(doy))

    # Load data
    data = pd.read_table(asciiloc, delim_whitespace=True)

    # Process data
    data['year'] = data['year'].astype(int)
    # Convert date info to datetime
    data['Time'] = pd.to_datetime(data['year'], format='%Y') + \
        pd.to_timedelta(data['day'] - 1, unit='d') + \
        pd.to_timedelta(data['hour'], unit='h') + \
        pd.to_timedelta(data['min'], unit='m') + \
        pd.to_timedelta(data['sec'], unit='s')
    data['ordinal'] = pd.DatetimeIndex(data['Time']).astype(np.int64)

    data = data.drop(['year', 'day', 'hour', 'min', 'sec', 'dechr'], axis=1)
    # Set zero values to nans
    data.replace(0.0, np.nan, inplace=True)

    # Save data to a hdf store
    saveloc = floc + fname + '.h5'
    data.to_hdf(saveloc, 'table', format='fixed', mode='w')
    return(data)


def mag_4hz(probe, starttime, endtime, verbose=True):
    """Read in 4Hz magnetic field data."""
    if isinstance(starttime, datetime.datetime):
        assert isinstance(endtime, datetime.datetime),\
            'Start time and end time must have same datatype'
        startdate = starttime.date()
        enddate = endtime.date()
    elif isinstance(starttime, datetime.date):
        assert isinstance(endtime, datetime.date),\
            'Start time and end time must have same datatype'
        startdate = starttime
        enddate = endtime

    data = []
    # Loop through years
    for year in range(startdate.year, enddate.year + 1):
        floc = helios_dir + '/helios' + probe + '/mag/4hz/'
        # Calculate start day
        startdoy = 1
        if year == startdate.year:
            startdoy = int(startdate.strftime('%j'))
        # Calculate end day
        enddoy = 366
        if year == enddate.year:
            enddoy = int(enddate.strftime('%j'))

        # Loop through days of year
        for doy in range(startdoy, enddoy + 1):
            hdfloc = floc + 'he' + probe + '1s' + str(year - 1900) +\
                str(doy).zfill(3) + '.h5'
            if not os.path.isfile(hdfloc):
                # Data not processed yet, try to process and load it
                try:
                    data.append(fourHz_fromascii(probe, year, doy))
                    if verbose:
                        print(year, doy, '4Hz data processed')
                except ValueError as err:
                    if str(err)[0:15] == 'No raw mag data':
                        if verbose:
                            print(year, doy, 'No raw mag data')
                    else:
                        raise
            else:
                # Load data from already processed file
                data.append(pd.read_hdf(hdfloc, 'table'))
    if data == []:
        raise ValueError('No raw mag data available')
    data = pd.concat(data, ignore_index=True)
    # If given datetimes, filter data
    if isinstance(starttime, datetime.datetime):
        data = data[(data['Time'] > starttime) & (data['Time'] < endtime)]

    if data.empty:
        raise ValueError('No raw mag data available')
    return(data)


def fourHz_fromascii(probe, year, doy):
    """Read in a single day of 4Hz magnetic field data."""
    floc = helios_dir + '/helios' + probe + '/mag/4hz/'
    fname = 'he' + probe + '1s' + str(year - 1900) + str(doy).zfill(3)
    # For some reason the last number in the filename is the hour at which
    # data starts from on that day... this means a loop to check each hour
    for i in range(0, 24):
        asciiloc = floc + fname + str(i).zfill(2) + '.asc'
        if os.path.isfile(asciiloc):
            break
        elif i == 23:
            raise ValueError('No raw mag data available for probe ' + probe +
                             ', Year: ' + str(year) + ' doy: ' + str(doy))

    # Read in data
    headings = ['Time', 'Bx', 'By', 'Bz']
    widths = [24, 16, 15, 15]
    data = pd.read_fwf(asciiloc, names=headings, header=None, widths=widths,
                       delim_whitespace=True)

    # Convert date info to datetime
    data['Time'] = pd.to_datetime(data['Time'], format='%Y-%m-%dT%H:%M:%S')
    data['ordinal'] = pd.DatetimeIndex(data['Time']).astype(np.int64)

    # Save data to a hdf store
    saveloc = floc + fname + '.h5'
    data.to_hdf(saveloc, 'table', format='fixed', mode='w')
    return(data)


def mag_ness(probe, starttime, endtime):
    """
    Read in 6 second magnetic field data

    starttime and endtime can either be datetime.date or datetime.datetime
    If they are datetime.date, load whole days inclusive of dates given
    """
    if isinstance(starttime, datetime.datetime):
        assert isinstance(endtime, datetime.datetime),\
            'Start time and end time must have same datatype'
        startdate = starttime.date()
        enddate = endtime.date()
    elif isinstance(starttime, datetime.date):
        assert isinstance(endtime, datetime.date),\
            'Start time and end time must have same datatype'
        startdate = starttime
        enddate = endtime

    data = []
    # Loop through years
    for year in range(startdate.year, enddate.year + 1):
        floc = helios_dir + '/helios' + probe + '/mag/6sec_ness/' + str(year) + '/'
        # Calculate start day
        startdoy = 1
        if year == startdate.year:
            startdoy = int(startdate.strftime('%j'))
        # Calculate end day
        enddoy = 366
        if year == enddate.year:
            enddoy = int(enddate.strftime('%j'))

        # Loop through days of year
        for doy in range(startdoy, enddoy + 1):
            hdfloc = floc + 'h' + probe + str(year - 1900) +\
                str(doy).zfill(3) + '.h5'
            if not os.path.isfile(hdfloc):
                # Data not processed yet, try to process and load it
                try:
                    data.append(mag_ness_fromascii(probe, year, doy))
                    print(year, doy, 'Ness data processed')
                except ValueError:
                    print(year, doy, 'No raw mag data')
            else:
                # Load data from already processed file
                data.append(pd.read_hdf(hdfloc, 'table'))

    if data == []:
        raise ValueError('No raw mag data available')
    data = pd.concat(data)
    # If given datetimes, filter data
    if isinstance(starttime, datetime.datetime):
        data = data[(data['Time'] > starttime) & (data['Time'] < endtime)]

    if data.empty:
        raise ValueError('No raw mag data available')
    return(data)


def mag_ness_fromascii(probe, year, doy):
    """Read in a single day of 6 second magnetic field data.s"""
    floc = helios_dir + '/helios' + probe + '/mag/6sec_ness/' + str(year) + '/'
    fname = 'h' + probe + str(year - 1900) + str(doy).zfill(3)
    asciiloc = floc + fname + '.asc'
    if not os.path.isfile(asciiloc):
        raise ValueError('No raw mag data available for probe ' + probe +
                         ', Year: ' + str(year) + ' DOY: ' + str(doy))

    # Read in data
    headings = ['probe', 'year', 'doy', 'hour', 'minute', 'second', 'naverage',
                'Bx', 'By', 'Bz', '|B|', 'sigma_Bx', 'sigma_By', 'sigma_Bz']

    colspecs = [(1, 2), (2, 4), (4, 7), (7, 9), (9, 11), (11, 13), (13, 15),
                (15, 22), (22, 29), (29, 36), (36, 42), (42, 48), (48, 54),
                (54, 60)]
    data = pd.read_fwf(asciiloc, names=headings, header=None, colspecs=colspecs)

    # Process data
    data['year'] += 1900
    # Convert date info to datetime
    data['Time'] = pd.to_datetime(data['year'], format='%Y') + \
        pd.to_timedelta(data['doy'] - 1, unit='d') + \
        pd.to_timedelta(data['hour'], unit='h') + \
        pd.to_timedelta(data['minute'], unit='m') + \
        pd.to_timedelta(data['second'], unit='s')
    data['ordinal'] = pd.DatetimeIndex(data['Time']).astype(np.int64)
    data = data.drop(['year', 'doy', 'hour', 'minute', 'second'], axis=1)

    # Save data to a hdf store
    saveloc = floc + fname + '.h5'
    data.to_hdf(saveloc, 'table', format='fixed', mode='w')
    return(data)


def trajectory(probe, startdate, enddate):
    """Read in trajectory data."""
    data = []
    headings = ['Year', 'doy', 'Hour', 'Carrrot', 'r', 'selat', 'selon',
                'hellat', 'hellon', 'hilon', 'escang', 'code']
    colspecs = [(0, 3), (4, 7), (8, 10), (11, 15), (16, 22), (23, 30), (31, 37),
                (38, 44), (45, 51), (52, 58), (59, 65), (66, 67)]
    # Loop through years
    for i in range(startdate.year, enddate.year + 1):
        floc = helios_dir + '/helios' + probe + '/traj/'
        fname = 'he' + probe + 'trj' + str(i - 1900) + '.asc'

        # Read in data
        try:
            thisdata = pd.read_fwf(floc + fname, names=headings, header=None,
                                   colspecs=colspecs)
        except OSError:
            continue

        thisdata['Year'] += 1900

        # Convert date info to datetime
        thisdata['Date'] = pd.to_datetime(thisdata['Year'], format='%Y') + \
            pd.to_timedelta(thisdata['doy'] - 1, unit='d') + \
            pd.to_timedelta(thisdata['Hour'], unit='h')
        thisdata['ordinal'] = pd.DatetimeIndex(thisdata['Date']).astype(np.int64)

        # Calculate cartesian positions
        thisdata['x'] = thisdata['r'] * np.cos(thisdata['selat']) * np.cos(thisdata['selon'])
        thisdata['y'] = thisdata['r'] * np.cos(thisdata['selat']) * np.sin(thisdata['selon'])
        thisdata['z'] = thisdata['r'] * np.sin(thisdata['selat'])

        thisdata = thisdata.drop(['Year', 'doy', 'Hour'], axis=1)
        data.append(thisdata)

    data = pd.concat(data)
    data = data[data['Date'] > startdate]
    data = data[data['Date'] < enddate]
    return(data)
