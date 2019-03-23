"""
Methods for importing data from the WIND spacecraft.
All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/wind.
See https://wind.nasa.gov/data_sources.php for more information on different
data products.
"""
import pathlib as path

import pandas as pd
import numpy as np
import astropy.units as u
import cdflib
import datetime as dt
from collections import OrderedDict
import warnings

from heliopy.data import cdasrest
from heliopy.data import util
from heliopy import config

data_dir = path.Path(config['download_dir'])
wind_dir = data_dir / 'wind'
use_hdf = config['use_hdf']
remote_wind_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/wind/'


def _docstring(identifier, description):
    return cdasrest._docstring(identifier, 'W', description)


def _wind(starttime, endtime, identifier, units=None,
          warn_missing_units=False, badvalues=None):
    """
    Generic method for downloading ACE data.
    """
    dataset = 'wi'
    return cdasrest._process_cdas(starttime, endtime, identifier, dataset,
                                  wind_dir,
                                  units=units,
                                  badvalues=badvalues,
                                  warn_missing_units=warn_missing_units)


# Actual download functions start here
def swe_h1(starttime, endtime):
    identifier = 'WI_H1_SWE'
    badvalues = 99999.9
    units = OrderedDict([('year', u.year),
                         ('fit_flag', u.dimensionless_unscaled),
                         ('ChisQ_DOF_nonlin', u.dimensionless_unscaled)])
    return _wind(starttime, endtime, identifier,
                 units=units, badvalues=badvalues)


swe_h1.__doc__ = _docstring(
    'WI_H1_SWE', '92-second Solar Wind Alpha and Proton Anisotropy Analysis')


def mfi_h0(starttime, endtime):
    identifier = 'WI_H0_MFI'
    units = OrderedDict([('Bx_gse', u.nT), ('By_gse', u.nT),
                        ('Bz_gse', u.nT)])
    return _wind(starttime, endtime, identifier,
                 units=units)


mfi_h0.__doc__ = _docstring(
    'WI_H0_MFI', 'Composite magnetic field')


def mfi_h2(starttime, endtime):
    identifier = 'WI_H2_MFI'
    units = OrderedDict([('Bx_gse', u.nT), ('By_gse', u.nT),
                        ('Bz_gse', u.nT)])
    return _wind(starttime, endtime, identifier,
                 units=units)


mfi_h2.__doc__ = _docstring(
    'WI_H2_MFI', 'High resolution magnetic field')


def threedp_pm(starttime, endtime):
    identifier = 'WI_PM_3DP'
    return _wind(starttime, endtime, identifier)


threedp_pm.__doc__ = _docstring(
    'WI_PM_3DP', '1 spin resolution ion (proton and alpha) moment')


def threedp_e0_emfits(starttime, endtime):
    identifier = 'WI_EMFITS_E0_3DP'
    return _wind(starttime, endtime, identifier)


threedp_e0_emfits.__doc__ = _docstring(
    'WI_EMFITS_E0_3DP', 'Electron moment')


# Old (non-CDAS) functions start here
_deprecation_msg = ("WIND pitch angle data products are deprecated since "
                    "version 0.6.7 and will be removed in version 0.7")


def swe_h3(starttime, endtime):
    """
    Import 'h3' solar wind electron data product from WIND.
    Electron pitch angle files providing electron fluxes at 30 directional bins
    relative to the instantaneous magnetic field direction at 13 different
    energy levels
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
    warnings.warn(_deprecation_msg, DeprecationWarning)
    relative_dir = path.Path('swe') / 'swe_h3'
    # Get directories and filenames
    dirs = []
    fnames = []
    units = OrderedDict([('Angle', u .deg),
                        ('Energy', u.eV),
                        ('df', u.cm/u.s)])
    daylist = util._daysplitinterval(starttime, endtime)
    for day in daylist:
        date = day[0]
        filename = 'wi_h3_swe_{}{:02}{:02}_v[0-9][0-9]'.format(
            date.year, date.month, date.day)
        fnames.append(filename)
        local_dir = relative_dir / str(date.year)
        dirs.append(local_dir)
    extension = '.cdf'
    local_base_dir = wind_dir
    remote_base_url = remote_wind_dir
    distkeys = []
    for i in range(0, 13):
        distkeys.append('f_pitch_E' + str(i).zfill(2))
    anglelabels = []
    for i in range(0, 30):
        anglelabels.append((i + 0.5) * np.pi / 30)
    timekey = 'Epoch'
    energykey = 'Ve'

    def download_func(*args):
        util._download_remote_unknown_version(*args)

    def processing_func(cdf):

        df = util.pitchdist_cdf2df(cdf, distkeys, energykey, timekey,
                                   anglelabels)
        df = df.reset_index(level=['Energy', 'Angle'])
        return df

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)


def threedp_sfpd(starttime, endtime):
    """
    Import 'sfpd' wind data.
    12 second energetic electron pitch-angle energy spectra from the foil SST.

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
    warnings.warn(_deprecation_msg, DeprecationWarning)
    # Directory relative to main WIND data directory
    relative_dir = path.Path('3dp') / '3dp_sfpd'
    daylist = util._daysplitinterval(starttime, endtime)
    fnames = []
    dirs = []
    units = OrderedDict([('Energy', u.eV),
                         ('Bx', u.nT),
                         ('By', u.nT),
                         ('Bz', u.nT),
                         ('Pitch angle', u.deg),
                         ('Flux', (u.cm**2 * u.sr * u.eV * u.s)**-1)])
    extension = '.cdf'
    for (date, _, _) in daylist:
        this_relative_dir = relative_dir / str(date.year)
        dirs.append(this_relative_dir)
        filename = 'wi_sfpd_3dp_{:{dfmt}}_v02'.format(
            date, dfmt='%Y%m%d')
        fnames.append(filename)

    local_base_dir = wind_dir
    remote_base_url = remote_wind_dir

    def download_func(*args):
        util._download_remote_unknown_version(*args)

    def processing_func(cdf):
        data_today = []
        # Loop through each timestamp to build up fluxes
        for non_empty_var in list(cdf.cdf_info().keys()):
            if 'variable' in non_empty_var.lower():
                if len(cdf.cdf_info()[non_empty_var]) > 0:
                    break

        index_ = cdf.varget('Epoch')[...]
        index_ = cdflib.cdfepoch.breakdown(index_)
        index_ = np.asarray([dt.datetime(*x) for x in index_])
        energies_ = cdf.varget('ENERGY')[...]
        angles_ = cdf.varget('PANGLE')[...]
        fluxes_ = cdf.varget('FLUX')[...]
        magfield_ = cdf.varget('MAGF')[...]
        for i, time in enumerate(index_):
            energies = energies_[i, :]
            angles = angles_[i, :]
            fluxes = fluxes_[i, :, :]
            magfield = magfield_[i, :]
            index = pd.MultiIndex.from_product(
                ([time], energies, angles),
                names=['Time', 'Energy', 'Pitch angle'])
            df = pd.DataFrame(fluxes.ravel(), index=index, columns=['Flux'])
            df = df.reset_index(level=['Energy', 'Pitch angle'])
            df['Bx'] = magfield[0]
            df['By'] = magfield[1]
            df['Bz'] = magfield[2]
            data_today.append(df)
        data_today = pd.concat(data_today)
        data_today = data_today.sort_index()
        return data_today

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)
