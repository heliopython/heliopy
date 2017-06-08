"""
Methods for importing data from the IMP spacecraft.

All data is publically available at ftp://cdaweb.gsfc.nasa.gov/pub/data/imp/
"""
import os
import pandas as pd
from datetime import datetime

import heliopy.time as spacetime
from heliopy.data import helper
from heliopy import config

data_dir = config['DEFAULT']['download_dir']
use_hdf = config['DEFAULT']['use_hdf']
imp_url = 'ftp://cdaweb.gsfc.nasa.gov/pub/data/imp/'
imp_dir = data_dir + '/imp'
valid_probes = ['1', '2', '3', '4', '5', '6', '7', '8']


def merged(probe, starttime, endtime, verbose=False):
    """
    Import merged plasma data. See
    ftp://cdaweb.gsfc.nasa.gov/pub/data/imp/imp8/merged/00readme.txt
    for information on variables.

    Parameters
    ----------
        probe : string
            Probe number.
        starttime : datetime
            Start of interval.
        endtime : datetime
            End of interval.
        verbose : bool, optional
            If ``True``, print information whilst loading. Default is
            ``False``.

    Returns
    -------
        data : DataFrame
            Requested data.
    """
    data = []
    startyear = starttime.year
    endyear = endtime.year
    # Loop through years
    for year in range(startyear, endyear + 1):
        if year == startyear:
            startmonth = starttime.month
        else:
            startmonth = 1

        if year == endyear:
            endmonth = endtime.month
        else:
            endmonth = 12

        # Loop through months
        for month in range(startmonth, endmonth + 1):
            print('Loading IMP merged probe {}, {:02d}/{}'.format(probe, month,
                                                                  year))
            intervalstring = str(year) + str(month).zfill(2)
            filename = 'imp_min_merge' + intervalstring + '.asc'
            # Location of file relative to local directory or remote url
            relative_loc = os.path.join('imp' + probe,
                                        'merged')

            local_dir = os.path.join(imp_dir, relative_loc)
            hdffile = os.path.join(local_dir, filename[:-3] + 'hdf')
            if os.path.isfile(hdffile):
                data.append(pd.read_hdf(hdffile))
                continue

            remote_url = imp_url + relative_loc
            f = helper.load(filename, local_dir, remote_url)
            readargs = {'names': ['Year', 'doy', 'Hour', 'Minute', 'sw_flag',
                                  'x_gse', 'y_gse', 'z_gse', 'y_gsm', 'z_gsm',
                                  'Nm', 'FCm', 'DWm',
                                  '<|B|>', '|<B>|', '<B_lat>', '<B_long>',
                                  'Bx_gse', 'By_gse', 'Bz_gse',
                                  'By_gsm', 'Bz_gsm',
                                  'sigma|B|', 'sigma B',
                                  'sigma B_x', 'sigma B_y', 'sigma B_z',
                                  'plas_reg', 'Npp', 'FCp', 'DWp',
                                  'v_fit',
                                  'vx_fit_gse', 'vy_fit_gse', 'vz_fit_gse',
                                  'vlong_fit', 'vlat_fit',
                                  'np_fit', 'Tp_fit',
                                  'v_mom',
                                  'vx_mom_gse', 'vy_mom_gse', 'vz_mom_gse',
                                  'vlong_mom', 'vlat_mom',
                                  'np_mom', 'Tp_mom'],
                        'na_values': ['9999', '999', '99', '99', '9',
                                      '9999.99', '9999.99', '9999.99',
                                      '9999.99', '9999.99',
                                      '9', '99', '9.99', '9999.99', '9999.99',
                                      '9999.99', '9999.99',
                                      '9999.99', '9999.99',
                                      '9999.99', '9999.99',
                                      '9999.99', '9999.99',
                                      '9999.99',
                                      '9999.99', '9999.99', '9999.99',
                                      '9', '9', '99', '9.99',
                                      '9999.9', '9999.9', '9999.9', '9999.9',
                                      '9999.9', '9999.9', '9999.9', '9999999.',
                                      '9999.9', '9999.9', '9999.9', '9999.9',
                                      '9999.9', '9999.9',
                                      '9999.9', '9999999.'],
                        'delim_whitespace': True}
            # Read in data
            thisdata = pd.read_table(f, **readargs)
            thisdata['Time'] = (pd.to_datetime(thisdata['Year'], format='%Y') +
                                pd.to_timedelta(thisdata['doy'] - 1,
                                                unit='d') +
                                pd.to_timedelta(thisdata['Hour'], unit='h') +
                                pd.to_timedelta(thisdata['Minute'], unit='m'))
            if use_hdf:
                thisdata.to_hdf(hdffile, key='distparams', mode='w')
            data.append(thisdata)

    return helper.timefilter(data, starttime, endtime)


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
        hdffname = filename[:-3] + '.hdf'
        # Location of file relative to local directory or remote url
        relative_loc = 'imp' + probe + '/mag/mag_320msec_cdaweb/' +\
            str(date.year)

        local_dir = os.path.join(imp_dir, relative_loc)
        hdffile = os.path.join(local_dir, hdffname)
        if os.path.exists(hdffile):
            thisdata = pd.read_hdf(hdffile)
            data.append(thisdata)
            continue

        remote_url = imp_url + relative_loc
        cdf = helper.load(filename, local_dir, remote_url)
        keys = {'B': '|B|',
                'BX': 'Bx',
                'BY': 'By',
                'BZ': 'Bz',
                'Epoch': 'Time'}
        thisdata = helper.cdf2df(cdf, 'Epoch', keys)
        data.append(thisdata)
        if use_hdf:
            thisdata.to_hdf(hdffile, key='merged', mode='w')

    data = pd.concat(data)
    data = data[(data['Time'] > startTime) & (data['Time'] < endTime)]
    return data
