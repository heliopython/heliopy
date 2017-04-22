"""
Methods for importing data from the IMP spacecraft.

All data is publically available at ftp://cdaweb.gsfc.nasa.gov/pub/data/imp/
"""
import os
import pandas as pd

import heliopy.time as spacetime
from heliopy.data import helper
from heliopy import config

data_dir = config['DEFAULT']['download_dir']
imp_url = 'ftp://cdaweb.gsfc.nasa.gov/pub/data/imp/'
imp_dir = data_dir + '/imp'
valid_probes = ['1', '2', '3', '4', '5', '6', '7', '8']


def mitplasma_h0(probe, starttime, endtime):
    """
    Import mit h0 plasma data.

    Parameters
    ----------
        probe : string
            Probe number.
        starttime : datetime
            Start of interval.
        endtime : datetime
            End of interval.

    Returns
    -------
        data : DataFrame
            Requested data.
    """
    data = []
    dtimes = spacetime.daysplitinterval(starttime, endtime)
    # Loop through years
    for dtime in dtimes:
        date = dtime[0]
        intervalstring = str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2)
        filename = 'i' + probe + '_h0_mitplasma_' + intervalstring + '_v01.cdf'
        # Location of file relative to local directory or remote url
        relative_loc = 'imp' + probe + '/plasma_mit/mitplasma_h0/' +\
            str(date.year)

        local_dir = os.path.join(imp_dir, relative_loc)
        remote_url = imp_url + relative_loc

        cdf = helper.load(filename, local_dir, remote_url)
        keys = {'EW_flowangle_best': 'EW_flowangle_best',
                'EW_flowangle_mom': 'EW_flowangle_best',
                'Epoch': 'Time',
                'Flow_elevation_thresh': 'Flow_elevation_thresh',
                'Flow_elevation_threshsp': 'Flow_elevation_threshsp',
                'Region': 'Region',
                'V_fit': 'V_fit',
                'V_mom': 'V_fit',
                'mode': 'mode',
                'protonV_thermal_fit': 'protonV_thermal_fit',
                'protonV_thermal_mom': 'protonV_thermal_fit',
                'proton_density_fit': 'proton_density_fit',
                'proton_density_mom': 'proton_density_mom',
                'xyzgse': ['x_gse', 'y_gse', 'z_gse'],
                'ygsm': 'ygsm',
                'zgsm': 'zgsm'}
        thisdata = helper.cdf2df(cdf, 'Epoch', keys)
        data.append(thisdata)

    data = pd.concat(data)
    data = data[(data['Time'] > starttime) & (data['Time'] < endtime)]
    return data


def mag320ms(probe, startTime, endTime):
    """
    Import 320ms cadence magnetic field data.

    Parameters
    ----------
        probe : string
            Probe number.
        starttime : datetime
            Start of interval.
        endtime : datetime
            End of interval.

    Returns
    -------
        data : DataFrame
            Requested data.
    """
    data = []
    dtimes = spacetime.daysplitinterval(startTime, endTime)
    # Loop through years
    for dtime in dtimes:
        date = dtime[0]
        intervalstring = str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2)
        filename = 'i8_320msec_mag_' + intervalstring + '_v01.cdf'
        # Location of file relative to local directory or remote url
        relative_loc = 'imp' + probe + '/mag/mag_320msec_cdaweb/' +\
            str(date.year)

        local_dir = os.path.join(imp_dir, relative_loc)
        remote_url = imp_url + relative_loc

        cdf = helper.load(filename, local_dir, remote_url)
        keys = {'B': '|B|',
                'BX': 'Bx',
                'BY': 'By',
                'BZ': 'Bz',
                'Epoch': 'Time'}
        thisdata = helper.cdf2df(cdf, 'Epoch', keys)
        data.append(thisdata)

    data = pd.concat(data)
    data = data[(data['Time'] > startTime) & (data['Time'] < endTime)]
    return data
