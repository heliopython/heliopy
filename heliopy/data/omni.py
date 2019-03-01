"""
Methods for importing data from the OMNI.

All data is publically available at
https://cdaweb.gsfc.nasa.gov/pub/data/omni.
"""
import pathlib as path

import pandas as pd
import astropy.units as u
import datetime as dt
from collections import OrderedDict

from heliopy.data import util
from heliopy import config

data_dir = path.Path(config['download_dir'])
omni_dir = data_dir / 'omni'
omni_url = 'https://cdaweb.gsfc.nasa.gov/pub/data/omni/'


def low(starttime, endtime, try_download=True):
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

    # Directory relative to main OMNI data directory
    local_base_dir = omni_dir / 'low'
    remote_base_url = omni_url + '/low_res_omni'
    dirs = []
    fnames = []
    names = ['Year', 'Decimal Day', 'Hour', 'Bartels Rotation Number',
             'ID IMF Spacecraft', 'ID SW Plasma Spacecraft',
             'points(IMF Average)', 'points(Plasma Average)',
             '|B|', 'Magnitude of Avg Field Vector',
             'Lat. Angle of Aver. Field Vector',
             'Long. Angle of Aver. Field Vector', 'Bx GSE, GSM', 'By GSE',
             'Bz GSE', 'By GSM', 'Bz GSM', 'sigma |B|', 'sigma B', 'sigma Bx',
             'sigma By', 'sigma Bz', 'Proton Temperature',
             'Proton Density', 'Plasma Flow Speed', 'Plasma Flow Long. Angle',
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
    extension = '.dat'
    for year in range(starttime.year, endtime.year + 1):
        fnames.append("omni2_{}".format(year))
        dirs.append(local_base_dir)

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        url = '{}'.format(remote_base_url)
        util._download_remote(url,
                              fname + extension,
                              local_base_dir / directory)

    def processing_func(file):
        thisdata = pd.read_csv(file, names=names,
                               delim_whitespace=True)
        year = thisdata['Year'][0]
        day_list = list(thisdata['Decimal Day'])
        hour_list = list(thisdata['Hour'])
        len_ = len(thisdata)
        time_index = convert_datetime(year, day_list, hour_list, len_)
        thisdata['Time'] = pd.to_datetime(time_index)
        thisdata = thisdata.set_index('Time')
        thisdata = thisdata.drop(['Year', 'Decimal Day', 'Hour'], axis=1)
        return thisdata

    def convert_datetime(year, day_list, hour_list, len_):
        datetime_index = []
        base_date = dt.datetime(year, 1, 1, 0, 0, 0)
        for x in range(0, len_):
            time_delta = dt.timedelta(days=day_list[x] - 1, hours=hour_list[x])
            datetime_index.append(base_date + time_delta)
        return datetime_index

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)
