"""
Methods for importing data from the OMNI.

All data is publically available at
https://cdaweb.gsfc.nasa.gov/pub/data/omni.
"""
from collections import OrderedDict
from datetime import datetime, timedelta
import pathlib

import astropy.units as u
import numpy as np
import pandas as pd
import xarray as xr

from heliopy.data import util

omni_url = 'https://cdaweb.gsfc.nasa.gov/pub/data/omni/'


class _omniDownloader(util.Downloader):
    def __init__(self, units):
        self.units = units

    def intervals(self, starttime, endtime):
        return self.intervals_yearly(starttime, endtime)

    def fname(self, interval):
        year = interval.start.to_datetime().year
        return f'omni2_{year}.dat'

    def local_dir(self, interval):
        return pathlib.Path('omni')

    def download(self, interval):
        url = omni_url + '/low_res_omni'

        local_dir = self.local_path(interval).parent
        local_dir.mkdir(parents=True, exist_ok=True)
        fname = self.fname(interval)
        util._download_remote(url, fname, local_dir)

    def load_local_file(self, interval, product_list=None):
        names = ['Year', 'Decimal Day', 'Hour', 'Bartels Rotation Number',
                 'ID IMF Spacecraft', 'ID SW Plasma Spacecraft',
                 'points(IMF Average)', 'points(Plasma Average)',
                 '|B|', 'Magnitude of Avg Field Vector',
                 'Lat. Angle of Aver. Field Vector',
                 'Long. Angle of Aver. Field Vector', 'Bx GSE, GSM', 'By GSE',
                 'Bz GSE', 'By GSM', 'Bz GSM', 'sigma |B|', 'sigma B',
                 'sigma Bx', 'sigma By', 'sigma Bz', 'Proton Temperature',
                 'Proton Density', 'Plasma Flow Speed',
                 'Plasma Flow Long. Angle',
                 'Plasma Flow Lat. Angle', 'Na/Np', 'Flow Pressure', 'sigma T',
                 'sigma N', 'sigma V', 'sigma phi V', 'sigma theta V',
                 'sigma Na/Np', 'Electric Field', 'Plasma Beta',
                 'Alfven Mach Number', 'Kp', 'R', 'DST Index', 'AE Index',
                 'Proton Flux > 1MeV', 'Proton Flux > 2MeV',
                 'Proton Flux > 4MeV', 'Proton Flux > 10MeV',
                 'Proton Flux > 30MeV',
                 'Proton Flux > 60MeV', 'flag', 'ap index',
                 'f10.7 index', 'PC(N) index', 'AL index (Kyoto)',
                 'AU index (Kyoto)', 'Magnetosonic Mach No.']
        badvalues = [np.nan, np.nan, np.nan, 9999, 99, 99, 999, 999, 999.9,
                     999.9, 999.9, 999.9, 999.9, 999.9, 999.9, 999.9, 999.9,
                     999.9, 999.9,
                     999.9, 999.9, 999.9, 9999999., 999.9, 9999., 999.9, 999.9,
                     9.999, 99.99, 9999999., 999.9, 9999., 999.9, 999.9, 9.999,
                     999.99, 999.99, 999.9, 99, 999, 99999, 9999, 999999.99,
                     99999.99, 99999.99, 99999.99, 99999.99, 99999.99, np.nan,
                     999, 999.9, 999.9, 99999, 99999, 99.9]
        thisdata = pd.read_csv(self.local_path(interval), names=names,
                               delim_whitespace=True)
        for name, bad_value in zip(names, badvalues):
            if name in ['Year', 'Decimal Day', 'Hour']:
                continue
            thisdata[name] = thisdata[name].replace(bad_value, np.nan)
        year = thisdata['Year'][0]
        day_list = list(thisdata['Decimal Day'])
        hour_list = list(thisdata['Hour'])
        len_ = len(thisdata)
        time_index = self._convert_datetime(year, day_list, hour_list, len_)
        thisdata['Time'] = pd.to_datetime(time_index)
        thisdata = thisdata.set_index('Time')
        thisdata = thisdata.drop(['Year', 'Decimal Day', 'Hour'], axis=1)
        
        if product_list:
            prod_list = []
            for val in product_list:
                prod_list.append(val)
            thisdata = pd.DataFrame(thisdata,columns=prod_list)
            data = xr.DataArray(thisdata, coords = [time_index, prod_list], dims=['time', 'products'])
            data.attrs['Units']={}
            for product in prod_list:
                data.attrs['Units'][product] = self.units[product]
        else:
            thisdata = pd.DataFrame(thisdata)
            data = xr.Dataset({})
            for i, product in enumerate(thisdata.columns):
                data[product] = xr.DataArray(thisdata[product], 
                                coords = [time_index],
                                dims=['time'])
            data.attrs['Units'] = self.units        
        return data

    def _convert_datetime(self, year, day_list, hour_list, len_):
        datetime_index = []
        base_date = datetime(year, 1, 1, 0, 0, 0)
        for x in range(0, len_):
            time_delta = timedelta(days=day_list[x] - 1, hours=hour_list[x])
            datetime_index.append(base_date + time_delta)
        return datetime_index


def low(starttime, endtime, product_list=None, want_xr=False):
    """
    Import data from OMNI Web Interface.

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
        data : :class:`~sunpy.timeseries.TimeSeries`
    """
    sfu = u.def_unit('sfu', 10**-22 * u.m**-2 * u.Hz**-1)
    units = OrderedDict([('Bartels Rotation Number', u.dimensionless_unscaled),
                         ('ID IMF Spacecraft', u.dimensionless_unscaled),
                         ('ID SW Plasma Spacecraft', u.dimensionless_unscaled),
                         ('points(IMF Average)', u.dimensionless_unscaled),
                         ('points(Plasma Average)', u.dimensionless_unscaled),
                         ('|B|', u.nT),
                         ('Magnitude of Avg Field Vector', u.nT),
                         ('Lat. Angle of Aver. Field Vector', u.deg),
                         ('Long. Angle of Aver. Field Vector', u.deg),
                         ('Bx GSE, GSM', u.nT),
                         ('By GSE', u.nT),
                         ('Bz GSE', u.nT),
                         ('By GSM', u.nT),
                         ('Bz GSM', u.nT),
                         ('sigma |B|', u.nT),
                         ('sigma B', u.nT),
                         ('sigma Bx', u.nT),
                         ('sigma By', u.nT),
                         ('sigma Bz', u.nT),
                         ('Proton Temperature', u.K),
                         ('Proton Density', u.cm**-3),
                         ('Plasma Flow Speed', u.km / u.s),
                         ('Plasma Flow Long. Angle', u.deg),
                         ('Plasma Flow Lat. Angle', u.deg),
                         ('Na/Np', u.dimensionless_unscaled),
                         ('Flow Pressure', u.nPa),
                         ('sigma T', u.K),
                         ('sigma N', u.cm**-3),
                         ('sigma V', u.km / u.s),
                         ('sigma phi V', u.deg),
                         ('sigma theta V', u.deg),
                         ('sigma Na/Np', u.dimensionless_unscaled),
                         ('Electric Field', u.mV / u.m),
                         ('Plasma Beta', u.dimensionless_unscaled),
                         ('Alfven Mach Number', u.dimensionless_unscaled),
                         ('Kp', u.dimensionless_unscaled),
                         ('R', u.dimensionless_unscaled),
                         ('AE Index', u.nT),
                         ('DST Index', u.nT),
                         ('Proton Flux > 1MeV', u.cm**-2),
                         ('Proton Flux > 2MeV', u.cm**-2),
                         ('Proton Flux > 4MeV', u.cm**-2),
                         ('Proton Flux > 10MeV', u.cm**-2),
                         ('Proton Flux > 30MeV', u.cm**-2),
                         ('Proton Flux > 60MeV', u.cm**-2),
                         ('flag', u.dimensionless_unscaled),
                         ('ap index', u.nT),
                         ('PC(N) index', u.dimensionless_unscaled),
                         ('AL index (Kyoto)', u.nT),
                         ('AU index (Kyoto)', u.nT),
                         ('Magnetosonic Mach No.', u.dimensionless_unscaled),
                         ('f10.7 index', sfu)])
    downloader = _omniDownloader(units)
    return downloader.load(starttime, endtime, product_list, want_xr)
