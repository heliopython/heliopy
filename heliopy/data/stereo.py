"""
Methods for importing data from the STEREO spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/stereo/.
The STEREO spacecraft homepage can be found at https://stereo.gsfc.nasa.gov/.
"""
from collections import OrderedDict
import pathlib
from datetime import datetime, timedelta
from dateutil.rrule import rrule, MONTHLY

import astropy.units as u
import pandas as pd

from heliopy import config
from heliopy.data import cdasrest
from heliopy.data import util

data_dir = pathlib.Path(config['download_dir'])
stereo_het_l2_dir = data_dir / 'stereo'

het_url = 'http://www.srl.caltech.edu/STEREO/DATA/HET/'

def _docstring(identifier, extra):
    return cdasrest._docstring_stereo(identifier, 'S', extra)

def _identifier_select(spacecraft):
    """
    Spacecraft selector for stereo
    """

    if spacecraft == 'sta':
        return 'STA'
    elif spacecraft == 'stb':
        return 'STB'
    else:
        raise ValueError("Invalid spacecraft, must be sta or stb")


def _stereo(starttime, endtime, spacecraft, identifier, units=None,
            warn_missing_units=True):
    """
    Generic method for downloading STEREO data.
    """

    directory = pathlib.Path("stereo", _identifier_select(spacecraft))
    badvalues = 1e-31
    return cdasrest.CDASDwonloader('ac', identifier, directory,
                                   badvalues=badvalues,
                                   warn_missing_units=warn_missing_units,
                                   units=units)


# Actual download functions start here
def mag_l1_rtn(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_MAG_RTN'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units).load(starttime, endtime)


mag_l1_rtn.__doc__ = _docstring('STA_L1_MAG_RTN',
                                    'STEREO IMPACT/MAG Magnetic Field Vectors')


def magplasma_l2(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L2_MAGPLASMA_1M'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units).load(starttime, endtime)


mag_l1_rtn.__doc__ = _docstring('STA_L2_MAGPLASMA_1M', 'STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data')


def magplasma_l2(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L2_MAGPLASMA_1M'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units).load(starttime, endtime)


magplasma_l2.__doc__ = _docstring('STA_L2_MAGPLASMA_1M', 'STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data')


def let_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_LET'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units).load(starttime, endtime)


let_l1.__doc__ = _docstring('STA_L1_LET',
                            'STEREO IMPACT/LET Level 1 Data')


def sept_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_SEPT'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled),
                         ('Heater_NS', u.deg_C),
                         ('Heater_E', u.deg_C)])
    sept = _stereo(starttime, endtime, spacecraft, identifier, units=units).load(starttime, endtime)
    sept.data['Epoch_NS'] = util.epoch_to_datetime(sept.data['Epoch_NS'].values)
    sept.data['Epoch_E'] = util.epoch_to_datetime(sept.data['Epoch_E'].values)

    return sept

sept_l1.__doc__ = _docstring('STA_L1_SEPT',
                             'STEREO IMPACT/SEPT Level 1 Data')


def sit_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_SIT'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units).load(starttime, endtime)


sit_l1.__doc__ = _docstring('STA_L1_SIT',
                            'STEREO IMPACT/SIT Level 1 Data')


def ste_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_STE'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units).load(starttime, endtime)


ste_l1.__doc__ = _docstring('STA_L1_STE',
                            'STEREO IMPACT/STE Level 1 Data')

def het_l1(starttime, endtime, spacecraft, timeres):
    """
    Import data from STEREO HET web Interface.

    Parameters
    ----------
        starttime : datetime
            Interval start time.
        endtime : datetime
            Interval end time.
        spacecraft: string
            Either "sta" or "stb"
        timeres: string
            Valid values are "1m", "15m", "1h", "12h", "1d"
            
    Returns
    -------
        data : :class:`~sunpy.timeseries.TimeSeries`
    """

    if timeres not in ("1m", "15m", "1h", "12h", "1d"):
        raise ValueError("Invalid time resolution, should be 1m, 15m, 1h, 12h or 1d")

    timedirs = {"1m": "1minute",
              "15m": "15minute",
              "1h": "1hour", 
              "12h": "12hour", 
              "1d": "1day"}
    
    sc_identifiers = {"STA": "Ahead",
                        "STB": "Behind"}
    identifier = _identifier_select(spacecraft)
    sc_ident = sc_identifiers[identifier]
        
    local_base_dir = stereo_dir / identifier / (identifier+"_L1_HET") / timedirs[timeres]
    remote_base_url = het_url + "/" + sc_ident + "/" + timedirs[timeres]

    names = ["Verse",
             "Year0", "Month0", "day0", "hour0minute0", 
             "Year1", "Month1", "day1", "hour1minute1", 
            "e_07_14", "e_07_14_unc",
            "e_14_28", "e_14_28_unc",
            "e_28_40", "e_28_40_unc",
            "p_136_151", "p_136_151_unc",
            "p_149_171", "p_149_171_unc",
            "p_170_193", "p_170_193_unc",
            "p_208_238", "p_208_238_unc",
            "p_238_264", "p_238_264_unc",
            "p_263_297", "p_263_297_unc",
            "p_295_334", "p_295_334_unc",
            "p_334_358", "p_334_358_unc",
            "p_355_405", "p_355_405_unc",
            "p_400_600", "p_400_600_unc",
            "p_600_1000", "p_600_1000_unc"]

    names_1m = ["Verse",
             "Year0", "Month0", "day0", "hour0minute0", 
            "e_07_14", "e_07_14_unc",
            "e_14_28", "e_14_28_unc",
            "e_28_40", "e_28_40_unc",
            "p_136_151", "p_136_151_unc",
            "p_149_171", "p_149_171_unc",
            "p_170_193", "p_170_193_unc",
            "p_208_238", "p_208_238_unc",
            "p_238_264", "p_238_264_unc",
            "p_263_297", "p_263_297_unc",
            "p_295_334", "p_295_334_unc",
            "p_334_358", "p_334_358_unc",
            "p_355_405", "p_355_405_unc",
            "p_400_600", "p_400_600_unc",
            "p_600_1000", "p_600_1000_unc"]

    units = OrderedDict([('Verse', u.dimensionless_unscaled),
                        ('Year0', u.dimensionless_unscaled),
                        ('Month0', u.dimensionless_unscaled),
                        ('day0', u.dimensionless_unscaled),
                        ('hour0minute0', u.dimensionless_unscaled),
                        ('Year1', u.dimensionless_unscaled),
                        ('Month1', u.dimensionless_unscaled),
                        ('day1', u.dimensionless_unscaled),
                        ('hour1minute1', u.dimensionless_unscaled),
                        ('e_07_14', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('e_07_14_unc', u.dimensionless_unscaled), 
                        ('e_14_28', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('e_14_28_unc', u.dimensionless_unscaled), 
                        ('e_28_40', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('e_28_40_unc', u.dimensionless_unscaled), 
                        ('p_136_151', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_136_151_unc', u.dimensionless_unscaled), 
                        ('p_149_171', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_149_171_unc', u.dimensionless_unscaled), 
                        ('p_170_193', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_170_193_unc', u.dimensionless_unscaled), 
                        ('p_208_238', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_208_238_unc', u.dimensionless_unscaled), 
                        ('p_238_264', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_238_264_unc', u.dimensionless_unscaled), 
                        ('p_263_297', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_263_297_unc', u.dimensionless_unscaled), 
                        ('p_295_334', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_295_334_unc', u.dimensionless_unscaled), 
                        ('p_334_358', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_334_358_unc', u.dimensionless_unscaled), 
                        ('p_355_405', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_355_405_unc', u.dimensionless_unscaled), 
                        ('p_400_600', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_400_600_unc', u.dimensionless_unscaled), 
                        ('p_600_1000', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
                        ('p_600_1000_unc', u.dimensionless_unscaled)])
             
    extension = "."+timeres
    # Create monthly filenames
    sttime = datetime(starttime.year, starttime.month, 1)
    fnames = [sc_ident[0]+dt.strftime("eH%y%b") for dt in rrule(MONTHLY, dtstart=sttime, until=endtime)]
    dirs = [local_base_dir]*len(fnames)
    
    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        url = '{}'.format(remote_base_url)
        util._download_remote(url,
                              fname + extension,
                              local_base_dir / directory)
    
    def processing_func(file):

        # Find end of header
        lines = file.readlines()
        endline = [i for i,l in enumerate(lines) if l=="#End\n"][0]
        file.seek(0)
        
        if timeres != "1m":
            thisdata = pd.read_table(file, names=names, delim_whitespace=True, header=endline)
        else:
            thisdata = pd.read_table(file, names=names_1m, delim_whitespace=True, header=endline)

        # Get minutes at the midpoint of the bin
        hour0, min0 = divmod(thisdata['hour0minute0'].values, 100)
        t0 = pd.to_datetime({'year': thisdata['Year0'].values,
                       'month': thisdata['Month0'].apply(lambda x: datetime.strptime(x, '%b').month).values,
                       'day': thisdata['day0'].values,
                        'hour': hour0,
                        'minute': min0})
        if timeres !="1m":
            hour1, min1 = divmod(thisdata['hour1minute1'].values, 100)
            t1 = pd.to_datetime({'year': thisdata['Year1'].values,
                           'month': thisdata['Month1'].apply(lambda x: datetime.strptime(x, '%b').month).values,
                           'day': thisdata['day1'].values,
                            'hour': hour1,
                            'minute': min1})
            dt = t1-t0
        else:
            dt = timedelta(seconds=60)
        
        thisdata['Time'] = t0+dt/2
        thisdata = thisdata.set_index('Time')
#        thisdata = thisdata.drop(["Verse", "Year0", "Month0", "day0", "hour0minute0"], axis=1)
#        if timeres != "1m":
#            thisdata = thisdata.drop(["Year1", "Month1", "day1", "hour1minute1"], axis=1)
        return thisdata

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)

