"""
Methods for importing Helios data.

In general the data are available form a number of sources (replace 'helios1'
with 'helios2' in url to change probe):

* Distribution functions - Not publically available
* Merged plasma/mangetic field - |merged_url|
* 6 second cadence magnetic field - |6s_mag_url|

.. |merged_url| replace::
    ftp://cdaweb.gsfc.nasa.gov/pub/data/helios/helios1/merged/
.. |6s_mag_url| replace::
    ftp://cdaweb.gsfc.nasa.gov/pub/data/helios/helios1/mag/6sec_ness/

If the data is publically available, it will be dowloaded automatically if it
doesn't exist locally.
"""
from datetime import date, time, datetime, timedelta
from ftplib import FTP
import os
import pathlib as path
from urllib.error import URLError
from collections import OrderedDict
import warnings

import astropy.constants as constants
import astropy.units as u
import numpy as np
import pandas as pd

from heliopy import config
from heliopy.data import util
from heliopy.data import cdasrest

data_dir = config['download_dir']
use_hdf = config['use_hdf']
helios_dir = os.path.join(data_dir, 'helios')


def _check_probe(probe):
    probe = str(probe)
    assert probe == '1' or probe == '2', 'Probe number must be 1 or 2'
    return probe


def _dist_file_dir(probe, year, doy):
    return os.path.join(helios_dir,
                        'helios{}'.format(probe),
                        'dist',
                        '{}'.format(year),
                        '{}'.format(int(doy)))


def _loaddistfile(probe, year, doy, hour, minute, second):
    """
    Method to load a Helios distribution file.

    Returns opened file and location of file if file exists. If file doesn't
    exist raises an OSError.

    Parameters
    ----------
    probe : int, string
        Helios probe to import data from. Must be 1 or 2.
    year : int
        Year
    doy : int
        Day of year
    hour : int
        Hour.
    minute : int
        Minute
    second : int
        Second

    Returns
    -------
    f : file
        Opened distribution function file
    filename : string
        Filename of opened file
    """
    probe = _check_probe(probe)
    # Work out location of file
    yearstring = str(year)[-2:]
    filedir = _dist_file_dir(probe, year, doy)
    filename = os.path.join(filedir,
                            'h' + probe + 'y' + yearstring +
                            'd' + str(doy).zfill(3) +
                            'h' + str(hour).zfill(2) +
                            'm' + str(minute).zfill(2) +
                            's' + str(second).zfill(2) + '_')

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


def _dist_filename_to_hms(path):
    """Given distribution filename, extract hour, minute, second"""
    # year = int(path[-21:-19]) + 1900
    # doy = int(path[-18:-15])
    hour = int(path[-14:-12])
    minute = int(path[-11:-9])
    second = int(path[-8:-6])
    return hour, minute, second


def integrated_dists(probe, starttime, endtime, verbose=False):
    """
    Returns the integrated distributions from experiments i1a and i1b in Helios
    distribution function files.

    The distributions are integrated over all angles and given as a function
    of proton velocity.

    Parameters
    ----------
    probe : int
        Helios probe to import data from. Must be 1 or 2.
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval
    verbose : bool, optional
        If ``True``, print information whilst loading. Default is ``False``.

    Returns
    -------
    distinfo : Series
        Infromation stored in the top of distribution function files.
    """
    extensions = ['hdm.0', 'hdm.1', 'ndm.0', 'ndm.1']
    distlist = {'a': [], 'b': []}
    starttime_orig = starttime

    # Loop through each day
    while starttime < endtime:
        year = starttime.year
        doy = starttime.strftime('%j')
        # Directory for today's distribution files
        dist_dir = _dist_file_dir(probe, year, doy)
        # Locaiton of hdf file to save to/load from
        hdffile = 'h' + probe + str(year) + str(doy).zfill(3) +\
            'integrated_dists.hdf'
        hdffile = os.path.join(dist_dir, hdffile)
        todays_dists = {'a': [], 'b': []}
        # Check if data is already saved
        if os.path.isfile(hdffile):
            for key in todays_dists:
                todays_dists[key] = pd.read_hdf(hdffile, key=key)
                distlist[key].append(todays_dists[key])
            starttime += timedelta(days=1)
            continue
        # If not saved, generate a derived file
        else:
            # Get every distribution function file present for this day
            for f in os.listdir(dist_dir):
                path = os.path.join(dist_dir, f)
                # Check for distribution function
                if path[-5:] in extensions:
                    hour, minute, second = _dist_filename_to_hms(path)
                    try:
                        a, b = integrated_dists_single(probe, year, doy,
                                                       hour, minute, second)
                    except RuntimeError as err:
                        strerr = 'No ion distribution function data in file'
                        if str(err) == strerr:
                            continue
                        raise err

                    t = datetime.combine(starttime.date(),
                                         time(hour, minute, second))
                    if verbose:
                        print(t)
                    dists = {'a': a, 'b': b}
                    for key in dists:
                        dist = dists[key]
                        dist['Time'] = t
                        dist = dist.set_index(['Time', 'v'], drop=True)
                        todays_dists[key].append(dist)
        # Go through a and b and concat all the data
        for key in todays_dists:
            todays_dists[key] = pd.concat(todays_dists[key])
            if use_hdf:
                todays_dists[key].to_hdf(hdffile, key=key, mode='a')
            distlist[key].append(todays_dists[key])
        starttime += timedelta(days=1)

    for key in distlist:
        distlist[key] = util.timefilter(distlist[key], starttime_orig, endtime)
    return distlist


def integrated_dists_single(probe, year, doy, hour, minute, second):
    """
    Returns the integrated distributions from experiments i1a and i1b in Helios
    distribution function files.

    The distributions are integrated over all angles and given as a function
    of proton velocity.

    Parameters
    ----------
    probe : int, string
        Helios probe to import data from. Must be 1 or 2.
    year : int
        Year
    doy : int
        Day of year
    hour : int
        Hour
    minute : int
        Minute.
    second : int
        Second

    Returns
    -------
    i1a : DataFrame
        i1a integrated distribution function.
    i1b : DataFrame
        i1b integrated distribution function.
    """
    probe = _check_probe(probe)
    f, _ = _loaddistfile(probe, year, doy, hour, minute, second)
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
    f.close()
    return i1a, i1b


def electron_dist_single(probe, year, doy, hour, minute, second,
                         remove_advect=False):
    """
    Read in 2D electron distribution function.

    Parameters
    ----------
    probe : int, string
        Helios probe to import data from. Must be 1 or 2.
    year : int
        Year
    doy : int
        Day of year
    hour : int
        Hour.
    minute : int
        Minute
    second : int
        Second
    remove_advect : bool, optional
        If ``False``, the distribution is returned in
        the spacecraft frame.

        If ``True``, the distribution is
        returned in the solar wind frame, by subtracting the spacecraft
        velocity from the velcoity of each bin. Note this significantly
        slows down reading in the distribution.

    Returns
    -------
    dist : DataFrame
        2D electron distribution function
    """
    probe = _check_probe(probe)
    f, filename = _loaddistfile(probe, year, doy, hour, minute, second)
    startline = None
    for i, line in enumerate(f):
        # Find start of electron distribution function
        if line[0:4] == ' 2-D':
            startline = i + 2
            # Throw away next line (just has max of distribution)
            f.readline()
            # Throw away next line (just has table headings)
            if f.readline()[0:27] == ' no electron data available':
                return None
            break
    nlines = None
    for i, line in enumerate(f):
        if 'Degree, Pizzo correction' in line:
            break
    nlines = i + 1
    if startline is None:
        return None
    ##########################################
    # Read and process electron distribution #
    ##########################################
    # Arguments for reading in data
    readargs = {'usecols': [0, 1, 2, 3, 4, 5],
                'names': ['Az', 'E_bin', 'pdf', 'counts', 'vx', 'vy'],
                'delim_whitespace': True,
                'skiprows': startline,
                'nrows': nlines}
    # Read in data
    dist = pd.read_table(filename, **readargs)
    if dist.empty:
        return None

    # Remove spacecraft abberation
    # Assumes that spacecraft motion is always in the ecliptic (x-y)
    # plane
    if remove_advect:
        params = distparams_single(probe, year, doy, hour, minute, second)
        dist['vx'] += params['helios_vr']
        dist['vy'] += params['helios_v']
    # Convert to SI units
    dist[['vx', 'vy']] *= 1e3
    dist['pdf'] *= 1e12
    # Calculate spherical coordinates of energy bins
    dist['|v|'], _, dist['phi'] =\
        util._cart2sph(dist['vx'], dist['vy'], 0)
    # Calculate bin energy assuming particles are electrons
    dist['E_electron'] = 0.5 * constants.m_e.value *\
        ((dist['|v|']) ** 2)

    # Convert to multi-index using Azimuth and energy bin
    dist = dist.set_index(['E_bin', 'Az'])
    f.close()
    return dist


def distparams(probe, starttime, endtime, verbose=False):
    """
    Read in distribution parameters found in the header of distribution files.

    Parameters
    ----------
    probe : int
        Helios probe to import data from. Must be 1 or 2.
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval
    verbose : bool, optional
        If ``True``, print information whilst loading. Default is ``False``.

    Returns
    -------
    distinfo : Series
        Infromation stored in the top of distribution function files
    """
    extensions = ['hdm.0', 'hdm.1', 'ndm.0', 'ndm.1']
    paramlist = []

    starttime_orig = starttime
    # Loop through each day
    while starttime < endtime:
        year = starttime.year
        doy = starttime.strftime('%j')
        # Directory for today's distribution files
        dist_dir = _dist_file_dir(probe, year, doy)
        # Locaiton of hdf file to save to/load from
        hdffile = 'h' + probe + str(year) + str(doy).zfill(3) +\
            'distparams.hdf'
        hdffile = os.path.join(dist_dir, hdffile)
        if os.path.isfile(hdffile):
            todays_params = pd.read_hdf(hdffile)
        elif not os.path.isdir(dist_dir):
            starttime += timedelta(days=1)
            continue
        else:
            todays_params = []
            # Get every distribution function file present for this day
            for f in os.listdir(dist_dir):
                path = os.path.join(dist_dir, f)
                # Check for distribution function
                if path[-5:] in extensions:
                    hour, minute, second = _dist_filename_to_hms(path)
                    if verbose:
                        print(starttime.date(), hour, minute, second)
                    p = distparams_single(probe, year, doy,
                                          hour, minute, second)
                    todays_params.append(p)

            todays_params = pd.concat(todays_params,
                                      ignore_index=True, axis=1).T
            todays_params = todays_params.set_index('Time', drop=False)
            # Convert columns to numeric types
            todays_params = todays_params.apply(pd.to_numeric, errors='ignore')
            todays_params['Time'] = pd.to_datetime(todays_params['Time'])
            if use_hdf:
                todays_params.to_hdf(hdffile, key='distparams', mode='w')
        paramlist.append(todays_params)
        starttime += timedelta(days=1)

    return util.timefilter(paramlist, starttime_orig, endtime)


def distparams_single(probe, year, doy, hour, minute, second):
    """
    Read in parameters from a single distribution function measurement.

    Parameters
    ----------
    probe : int, string
        Helios probe to import data from. Must be 1 or 2.
    year : int
        Year
    doy : int
        Day of year
    hour : int
        Hour
    minute : int
        Minute
    second : int
        Second

    Returns
    -------
    distparams : Series
        Distribution parameters from top of distribution function file.
    """
    probe = _check_probe(probe)
    f, _ = _loaddistfile(probe, year, doy, hour, minute, second)

    _, month, day = util.doy2ymd(year, doy)
    dtime = datetime(year, month, day, hour, minute, second)
    distparams = pd.Series(dtime, index=['Time'])
    # Ignore the Pizzo et. al. correction at top of file
    for _ in range(0, 3):
        f.readline()
    # Line of flags
    flags = f.readline().split()
    distparams['imode'] = int(flags[0])
    # Alternating energy/azimuth shift on?
    distparams['ishift'] = bool(flags[1])
    # Possibly H2 abberation shift?
    distparams['iperihelion_shift'] = bool(flags[2])
    # Indicates a HDM file which contained bad data (frames), but could be
    # handled as NDM file
    distparams['minus'] = int(flags[3])
    # 0 = no instrument, 1 = i1a, 2 = I3
    distparams['ion_instrument'] = int(flags[4])
    distparams['data_rate'] = 1 if ('hdm' in f.name) else 0

    # 2 lines of Helios location information
    location = f.readline().split()
    distparams['r_sun'] = float(location[0])     # Heliospheric distance (AU)
    distparams['clong'] = float(location[1])    # Carrington longitude (deg)
    distparams['clat'] = float(location[2])     # Carrington lattitude (deg)
    distparams['carrot'] = int(f.readline().split()[0])   # Carrington cycle

    # 2 lines of Earth location information
    earth_loc = f.readline().split()
    # Heliospheric distance (AU)
    distparams['earth_rsun'] = float(earth_loc[0])
    # Carrington longitude (deg)
    distparams['earth_clong'] = float(earth_loc[1])
    # Carrington lattitude (deg)
    distparams['earth_clat'] = float(earth_loc[2])
    earth_loc = f.readline().split()
    # Angle between Earth and Helios (deg)
    distparams['earth_he_angle'] = float(earth_loc[0])
    # Carrington rotation
    distparams['earth_carrot'] = int(earth_loc[1])

    # Helios velocity information
    helios_v = f.readline().split()
    # Helios radial velocity (km/s)
    distparams['helios_vr'] = float(helios_v[0]) * 1731
    # Helios tangential velocity (km/s)
    distparams['helios_v'] = float(helios_v[1]) * 1731

    # i1a integrated ion parameters
    i1a_proton_params = f.readline().split()
    # Proton number density (cm^-3)
    distparams['np_i1a'] = float(i1a_proton_params[0])
    # Proton velocity (km/s)
    distparams['vp_i1a'] = float(i1a_proton_params[1])
    # Proton temperature (K)
    distparams['Tp_i1a'] = float(i1a_proton_params[2])
    i1a_proton_params = f.readline().split()
    # Proton azimuth flow angle (deg)
    distparams['v_az_i1a'] = float(i1a_proton_params[0])
    # Proton elevation flow angle (deg)
    distparams['v_el_i1a'] = float(i1a_proton_params[1])
    assert distparams['v_az_i1a'] < 360,\
        'Flow azimuth must be less than 360 degrees'

    # i1a integrated alpha parameters (possibly all zero?)
    i1a_alpha_params = f.readline().split()
    # Alpha number density (cm^-3)
    distparams['na_i1a'] = float(i1a_alpha_params[0])
    # Alpha velocity (km/s)
    distparams['va_i1a'] = float(i1a_alpha_params[1])
    # Alpha temperature (K)
    distparams['Ta_i1a'] = float(i1a_alpha_params[2])

    # i1b integrated ion parameters
    i1b_proton_params = f.readline().split()
    # Proton number density (cm^-3)
    distparams['np_i1b'] = float(i1b_proton_params[0])
    # Proton velocity (km/s)
    distparams['vp_i1b'] = float(i1b_proton_params[1])
    # Proton temperature (K)
    distparams['Tp_i1b'] = float(i1b_proton_params[2])

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
    to_replace = {'Tp_i1a': [-1.0, 0],
                  'np_i1a': [-1.0, 0],
                  'vp_i1a': [-1.0, 0],
                  'Tp_i1b': [-1.0, 0],
                  'np_i1b': [-1.0, 0],
                  'vp_i1b': [-1.0, 0],
                  'sigmaBx': -0.01, 'sigmaBy': -0.01, 'sigmaBz': -0.01,
                  'Bx': 0.0, 'By': 0.0, 'Bz': 0.0,
                  'v_az_i1a': [-1, 0], 'v_el_i1a': [-1, 0],
                  'na_i1a': [-1, 0], 'va_i1a': [-1, 0], 'Ta_i1a': [-1, 0]}
    distparams = distparams.replace(to_replace, np.nan)
    f.close()
    return distparams


def electron_dists(probe, starttime, endtime, remove_advect=False,
                   verbose=False):
    """
    Return 2D electron distributions between *starttime* and *endtime*

    Parameters
    ----------
    probe : int
        Helios probe to import data from. Must be 1 or 2.
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval
    remove_advect : bool, optional
        If *False*, the distribution is returned in
        the spacecraft frame.

        If *True*, the distribution is
        returned in the solar wind frame, by subtracting the spacecraft
        velocity from the velcoity of each bin. Note this significantly
        slows down reading in the distribution.
    verbose : bool, optional
        If ``True``, print dates when loading files. Default is ``False``.

    Returns
    -------
    dists : DataFrame
        Electron distribution functions
    """
    extensions = ['hdm.0', 'hdm.1', 'ndm.0', 'ndm.1']
    distlist = []

    # Loop through each day
    starttime_orig = starttime
    while starttime < endtime:
        year = starttime.year
        doy = starttime.strftime('%j')
        if verbose:
            print('Loading electron dists from year', year, 'doy', doy)
        # Directory for today's distribution files
        dist_dir = _dist_file_dir(probe, year, doy)
        print(dist_dir)
        # If directory doesn't exist, print error and continue
        if not os.path.exists(dist_dir):
            print('No electron distributions available for year', year,
                  'doy', doy)
            starttime += timedelta(days=1)
            continue

        # Locaiton of hdf file to save to/load from
        hdffile = 'h' + probe + str(year) + str(doy).zfill(3) +\
            'electron_dists.hdf'
        hdffile = os.path.join(dist_dir, hdffile)
        if os.path.isfile(hdffile):
            todays_dist = pd.read_hdf(hdffile)
            distlist.append(todays_dist)
            starttime += timedelta(days=1)
            continue

        todays_dist = []
        # Get every distribution function file present for this day
        for f in os.listdir(dist_dir):
            path = os.path.join(dist_dir, f)
            # Check for distribution function
            if path[-5:] in extensions:
                hour, minute, second = _dist_filename_to_hms(path)
                try:
                    d = electron_dist_single(probe, year, doy,
                                             hour, minute, second)
                except RuntimeError as err:
                    strerr = 'No electron distribution function data in file'
                    if str(err) == strerr:
                        continue
                    raise err
                if d is None:
                    continue

                t = datetime.combine(starttime.date(),
                                     time(hour, minute, second))
                d['Time'] = t
                if verbose:
                    print(t)
                todays_dist.append(d)

        if todays_dist == []:
            starttime += timedelta(days=1)
            continue
        todays_dist = pd.concat(todays_dist)
        todays_dist = todays_dist.set_index('Time', append=True)
        if use_hdf:
            todays_dist.to_hdf(hdffile, key='electron_dists', mode='w')
        distlist.append(todays_dist)
        starttime += timedelta(days=1)

    if distlist == []:
        raise RuntimeError('No electron data available for times ' +
                           str(starttime_orig) + ' to ' + str(endtime))
    return util.timefilter(distlist, starttime_orig, endtime)


def ion_dists(probe, starttime, endtime, remove_advect=False, verbose=False):
    """
    Return 3D ion distributions between *starttime* and *endtime*

    Parameters
    ----------
    probe : int
        Helios probe to import data from. Must be 1 or 2.
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval
    remove_advect : bool, optional
        If *False*, the distribution is returned in
        the spacecraft frame.

        If *True*, the distribution is
        returned in the solar wind frame, by subtracting the spacecraft
        velocity from the velcoity of each bin. Note this significantly
        slows down reading in the distribution.
    verbose : bool, optional
        If ``True``, print dates when loading files. Default is ``False``.

    Returns
    -------
    distinfo : Series
        Infromation stored in the top of distribution function files.
    """
    extensions = ['hdm.0', 'hdm.1', 'ndm.0', 'ndm.1']
    distlist = []

    # Loop through each day
    starttime_orig = starttime
    while starttime < endtime:
        year = starttime.year
        doy = int(starttime.strftime('%j'))
        if verbose:
            print('Loading ion dists from year', year, 'doy', doy)
        # Directory for today's distribution files
        dist_dir = _dist_file_dir(probe, year, doy)
        # If directory doesn't exist, print error and continue
        if not os.path.exists(dist_dir):
            print('No ion distributions available for year', year, 'doy', doy)
            starttime += timedelta(days=1)
            continue

        # Locaiton of hdf file to save to/load from
        hdffile = 'h' + probe + str(year) + str(doy).zfill(3) +\
            'ion_dists.hdf'
        hdffile = os.path.join(dist_dir, hdffile)
        if os.path.isfile(hdffile):
            todays_dist = pd.read_hdf(hdffile)
            distlist.append(todays_dist)
            starttime += timedelta(days=1)
            continue

        todays_dist = []
        # Get every distribution function file present for this day
        for f in os.listdir(dist_dir):
            path = os.path.join(dist_dir, f)
            # Check for distribution function
            if path[-5:] in extensions:
                hour, minute, second = _dist_filename_to_hms(path)
                try:
                    d = ion_dist_single(probe, year, doy,
                                        hour, minute, second)
                except RuntimeError as err:
                    strerr = 'No ion distribution function data in file'
                    if str(err) == strerr:
                        continue
                    raise err

                t = datetime.combine(starttime.date(),
                                     time(hour, minute, second))
                d['Time'] = t
                if verbose:
                    print(t)
                todays_dist.append(d)

        if todays_dist == []:
            starttime += timedelta(days=1)
            continue
        todays_dist = pd.concat(todays_dist)
        todays_dist = todays_dist.set_index('Time', append=True)
        if use_hdf:
            todays_dist.to_hdf(hdffile, key='ion_dist', mode='w')
        distlist.append(todays_dist)
        starttime += timedelta(days=1)

    if distlist == []:
        raise RuntimeError('No data available for times ' +
                           str(starttime_orig) + ' to ' + str(endtime))
    return util.timefilter(distlist, starttime_orig, endtime)


def ion_dist_single(probe, year, doy, hour, minute, second,
                    remove_advect=False):
    """
    Read in ion distribution function.

    Parameters
    ----------
    probe : int, string
        Helios probe to import data from. Must be 1 or 2.
    year : int
        Year
    doy : int
        Day of year
    hour : int
        Hour
    minute : int
        Minute.
    second : int
        Second
    remove_advect : bool, optional
        If *False*, the distribution is returned in
        the spacecraft frame.

        If *True*, the distribution is
        returned in the solar wind frame, by subtracting the spacecraft
        velocity from the velcoity of each bin. Note this significantly
        slows down reading in the distribution.

    Returns
    -------
    dist : DataFrame
        3D ion distribution function
    """
    probe = _check_probe(probe)
    f, filename = _loaddistfile(probe, year, doy, hour, minute, second)

    nionlines = None   # Number of lines in ion distribution
    linesread = 0  # Stores the total number of lines read in the file
    # Loop through file to find end of ion distribution function
    for i, line in enumerate(f):
        # Find start of proton distribution function
        if line[0:23] == 'Maximum of distribution':
            ionstartline = i + 1
        # Find number of lines in ion distribution function
        if line[0:4] == ' 2-D':
            nionlines = i - ionstartline
            break

    linesread += i
    # Bizzare case where there are two proton distributions in one file,
    # or there's no electron data available
    for i, line in enumerate(f):
        if line[0:23] == 'Maximum of distribution' or\
           line[0:30] == '  1.2 Degree, Pizzo correction' or\
           line[0:30] == ' -1.2 Degree, Pizzo correction':
            warnings.warn("More than one ion distribution function found",
                          RuntimeWarning)
            # NOTE: Bodge
            linesread -= 1
            break

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
        raise RuntimeError('No ion distribution function data in file')

    # Arguments for reading in data
    readargs = {'usecols': [0, 1, 2, 3, 4, 5, 6, 7],
                'names': ['Az', 'El', 'E_bin', 'pdf', 'counts',
                          'vx', 'vy', 'vz'],
                'delim_whitespace': True,
                'skiprows': ionstartline,
                'nrows': nionlines}
    # Read in data
    dist = pd.read_table(filename, **readargs)

    # Remove spacecraft abberation
    # Assumes that spacecraft motion is always in the ecliptic (x-y)
    # plane
    if remove_advect:
        params = distparams_single(probe, year, doy, hour, minute, second)
        dist['vx'] += params['helios_vr']
        dist['vy'] += params['helios_v']
    # Convert to SI units
    dist[['vx', 'vy', 'vz']] *= 1e3
    dist['pdf'] *= 1e12
    # Calculate magnitude, elevation and azimuth of energy bins
    dist['|v|'], dist['theta'], dist['phi'] =\
        util._cart2sph(dist['vx'], dist['vy'], dist['vz'])
    # Calculate bin energy assuming particles are protons
    dist['E_proton'] = 0.5 * constants.m_p.value * ((dist['|v|']) ** 2)

    # Convert to multi-index using azimuth, elevation, and energy bins
    dist = dist.set_index(['E_bin', 'El', 'Az'])
    return dist


def corefit(probe, starttime, endtime, try_download=True):
    """
    Read in merged data set

    Parameters
    ----------
    probe : int, string
        Helios probe to import data from. Must be 1 or 2.
    starttime : datetime
        Interval start time
    endtime : datetime
        Interval end time
    try_download : bool, optional
        If ``False`` don't try to download data if it is missing locally.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Data set
    """
    probe = _check_probe(probe)
    dirs = []
    fnames = []
    units = OrderedDict([('B instrument', u.dimensionless_unscaled),
                        ('Bx', u.nT), ('By', u.nT), ('Bz', u.nT),
                        ('sigma B', u.nT),
                        ('Ion instrument', u.dimensionless_unscaled),
                        ('Status', u.dimensionless_unscaled),
                        ('Tp_par', u.K), ('Tp_perp', u.K),
                        ('carrot', u.dimensionless_unscaled),
                        ('r_sun', u.AU), ('clat', u.deg),
                        ('clong', u.deg), ('earth_he_angle', u.deg),
                        ('n_p', u.cm**-3), ('vp_x', u.km/u.s),
                        ('vp_y', u.km/u.s), ('vp_z', u.km/u.s),
                        ('vth_p_par', u.km/u.s), ('vth_p_perp', u.km/u.s)])
    daylist = util._daysplitinterval(starttime, endtime)
    for day in daylist:
        this_date = day[0]
        # Check that data for this day exists
        if probe == '1':
            if this_date < date(1974, 12, 12) or this_date > date(1985, 9, 4):
                continue
        if probe == '2':
            if this_date < date(1976, 1, 17) or this_date > date(1980, 3, 8):
                continue

        doy = int(this_date.strftime('%j'))
        year = this_date.year
        floc = (path.Path('E1_experiment') /
                'New_proton_corefit_data_2017' /
                'ascii' /
                'helios{}'.format(probe) /
                '{}'.format(year))
        dirs.append(floc)
        fname = 'h{}_{}_{:03}_corefit'.format(probe, year, doy)
        fnames.append(fname)

    extension = '.csv'
    local_base_dir = path.Path(helios_dir)
    remote_base_url = 'http://helios-data.ssl.berkeley.edu/data/'

    def download_func(remote_base_url, local_base_dir, directory,
                      fname, remote_fname, extension):
        remote_url = '{}{}'.format(remote_base_url, directory)
        util.load(fname + extension,
                  local_base_dir / directory,
                  remote_url)

    def processing_func(f):
        return pd.read_csv(f, parse_dates=['Time'])

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, try_download, units=units)


def _4hz_filename(probe, year, doy):
    # Returns 4hz filename WITHOUT extension
    return 'he{}1s{}{:03}'.format(probe, year - 1900, doy)


def mag_4hz(probe, starttime, endtime, try_download=True):
    """
    Read in 4Hz magnetic field data.

    Parameters
    ----------
    probe : int, string
        Helios probe to import data from. Must be 1 or 2.
    starttime : datetime
        Interval start time
    endtime : datetime
        Interval end time
    try_download : bool, optional
        If ``False`` don't try to download data if it is missing locally.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        4Hz magnetic field data set
    """
    probe = _check_probe(probe)
    local_base_dir = (path.Path(helios_dir) / 'E2_experiment' /
                      'Data_Cologne_Nov2016_bestdata' / 'HR' /
                      'helios{}'.format(probe))
    remote_base_url = 'apollo.ssl.berkeley.edu'
    extension = '.asc'
    dirs = []
    fnames = []
    units = OrderedDict([('Bx', u.nT), ('By', u.nT),
                        ('Bz', u.nT), ('|B|', u.nT)])

    daylist = util._daysplitinterval(starttime, endtime)
    for [day, _, _] in daylist:
        dirs.append('')
        doy = int(day.strftime('%j'))
        year = day.year
        fnames.append('he{}1s{}{:03}'.format(probe, year - 1900, doy))

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        local_dir = local_base_dir / directory
        remote_dir = ('pub/helios-data/E2_experiment/'
                      'Data_Cologne_Nov2016_bestdata/'
                      'HR/helios{}'.format(probe))
        remote_url = 'ftp://' + remote_base_url + '/' + remote_dir

        original_fname = fname
        fname = None
        # Because the filename contains a number between 0 and 24 at the end,
        # get a list of all the filenames and compare them to the filename
        # we want
        with FTP(remote_base_url) as ftp:
            ftp.login()
            remote_fnames = ftp.nlst(remote_dir)

        for remote_fname in remote_fnames:
            if original_fname in remote_fname:
                fname = remote_fname
                break
        if fname is None:
            raise util.NoDataError
        util._download_remote(remote_url, fname, local_base_dir)

        # Rename to a sensible and deterministic file name
        downloaded_path = (local_base_dir / fname).with_suffix(extension)
        new_path = (local_base_dir / original_fname).with_suffix(extension)
        downloaded_path.rename(new_path)

    def processing_func(f):
        # Read in data
        headings = ['Time', 'Bx', 'By', 'Bz', '|B|']
        cols = [0, 4, 5, 6, 7]
        data = pd.read_table(f, names=headings, header=None,
                             usecols=cols, delim_whitespace=True)

        # Convert date info to datetime
        data['Time'] = pd.to_datetime(data['Time'], format='%Y-%m-%dT%H:%M:%S')
        data = data.set_index('Time', drop=True)
        return data

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units,
                        try_download=try_download)


def mag_ness(probe, starttime, endtime, try_download=True):
    """
    Read in 6 second magnetic field data.

    Parameters
    ----------
    probe : int, string
        Helios probe to import data from. Must be 1 or 2.
    starttime : datetime
        Interval start time
    endtime : datetime
        Interval end time
    try_download : bool, optional
        If ``False`` don't try to download data if it is missing locally.

    Returns
    -------
    data : DataFrame
        6 second magnetic field data set
    """
    probe = _check_probe(probe)
    remote_base_url = ('http://helios-data.ssl.berkeley.edu/data/'
                       'E3_experiment/helios{}_6sec_ness/'.format(probe))
    local_base_dir = (path.Path(helios_dir) /
                      'E3_experiment' /
                      'helios{}_6sec_ness'.format(probe))
    dirs = []
    fnames = []
    extension = '.asc'
    units = OrderedDict([('probe', u.dimensionless_unscaled),
                         ('naverage', u.dimensionless_unscaled),
                         ('Bx', u.nT), ('By', u.nT), ('Bz', u.nT),
                         ('|B|', u.nT), ('sigma_Bx', u.nT),
                         ('sigma_By', u.nT), ('sigma_Bz', u.nT)])
    daylist = util._daysplitinterval(starttime, endtime)
    for [day, _, _] in daylist:
        year = day.year
        doy = int(day.strftime('%j'))
        dirs.append('{}'.format(day.year))
        fnames.append('h{}{}{:03}'.format(probe, year - 1900, doy))

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        remote_url = remote_base_url + str(directory)
        local_dir = local_base_dir / directory
        filename = fname + extension
        try:
            util._download_remote(remote_url, filename, local_dir)
        except URLError:
            raise util.NoDataError

    def processing_func(f):
        # Read in data
        headings = ['probe', 'year', 'doy', 'hour', 'minute', 'second',
                    'naverage', 'Bx', 'By', 'Bz', '|B|',
                    'sigma_Bx', 'sigma_By', 'sigma_Bz']

        colspecs = [(1, 2), (2, 4), (4, 7), (7, 9), (9, 11), (11, 13),
                    (13, 15), (15, 22), (22, 29), (29, 36), (36, 42), (42, 48),
                    (48, 54), (54, 60)]
        data = pd.read_fwf(f, names=headings, header=None,
                           colspecs=colspecs)

        # Process data
        data['year'] += 1900
        # Convert date info to datetime
        data['Time'] = pd.to_datetime(data['year'], format='%Y') + \
            pd.to_timedelta(data['doy'] - 1, unit='d') + \
            pd.to_timedelta(data['hour'], unit='h') + \
            pd.to_timedelta(data['minute'], unit='m') + \
            pd.to_timedelta(data['second'], unit='s')
        data = data.drop(['year', 'doy', 'hour', 'minute', 'second'], axis=1)
        data = data.set_index('Time', drop=False)
        return data

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units,
                        try_download=try_download)


def _docstring(identifier, extra):
    return cdasrest._docstring(identifier, 'M', extra)


def _helios(starttime, endtime, identifier, units=None, badvalues=None,
            warn_missing_units=True):
    """
    Generic method for downloading Helios data from CDAWeb.
    """
    dataset = 'helios'
    return cdasrest._process_cdas(starttime, endtime, identifier, dataset,
                                  helios_dir,
                                  units=units,
                                  badvalues=badvalues,
                                  warn_missing_units=warn_missing_units)


def merged(probe, starttime, endtime):
    identifier = f'HELIOS{probe}_40SEC_MAG-PLASMA'
    badvalues = [-1e31]
    return _helios(starttime, endtime, identifier, badvalues=badvalues,
                   warn_missing_units=False)


merged.__doc__ = _docstring(
    'HELIOS1_40SEC_MAG-PLASMA', 'merged magnetic field and plasma data.')
