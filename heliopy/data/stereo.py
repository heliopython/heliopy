"""
Methods for importing data from the STEREO spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/stereo/.
The STEREO spacecraft homepage can be found at https://stereo.gsfc.nasa.gov/.
"""
from collections import OrderedDict
import pathlib as path
from datetime import datetime, timedelta
from dateutil.rrule import rrule, MONTHLY

import astropy.units as u
import pandas as pd

from heliopy import config
from heliopy.data import cdasrest
from heliopy.data import util

data_dir = path.Path(config['download_dir'])
stereo_dir = data_dir / 'stereo'

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


def _stereo(starttime, endtime, dataset, identifier, units=None,
            warn_missing_units=True):
    """
    Generic method for downloading STEREO data.
    """
    badvalues = 1e-31
    return cdasrest._process_cdas(starttime, endtime, identifier, dataset,
                                  stereo_dir,
                                  units=units,
                                  badvalues=badvalues,
                                  warn_missing_units=warn_missing_units)


# Actual download functions start here
def mag_l1_rtn(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_MAG_RTN'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


mag_l1_rtn.__doc__ = _docstring('STA_L1_MAG_RTN',
                                    'STEREO IMPACT/MAG Magnetic Field Vectors')


def magplasma_l2(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L2_MAGPLASMA_1M'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


mag_l1_rtn.__doc__ = _docstring('STA_L2_MAGPLASMA_1M', 'STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data')


def magplasma_l2(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L2_MAGPLASMA_1M'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


magplasma_l2.__doc__ = _docstring('STA_L2_MAGPLASMA_1M', 'STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data')


def let_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_LET'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


let_l1.__doc__ = _docstring('STA_L1_LET',
                            'STEREO IMPACT/LET Level 1 Data')


def sept_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_SEPT'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled),
                         ('Heater_NS', u.deg_C),
                         ('Heater_E', u.deg_C)])
    sept = _stereo(starttime, endtime, spacecraft, identifier, units=units)
    sept.data['Epoch_NS'] = util.epoch_to_datetime(sept.data['Epoch_NS'].values)
    sept.data['Epoch_E'] = util.epoch_to_datetime(sept.data['Epoch_E'].values)

    return sept

sept_l1.__doc__ = _docstring('STA_L1_SEPT',
                             'STEREO IMPACT/SEPT Level 1 Data')


def sit_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_SIT'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


sit_l1.__doc__ = _docstring('STA_L1_SIT',
                            'STEREO IMPACT/SIT Level 1 Data')


def ste_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_STE'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


ste_l1.__doc__ = _docstring('STA_L1_STE',
                            'STEREO IMPACT/STE Level 1 Data')



def het(starttime, endtime, spacecraft, timeres):
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
    
    sc_ident = sc_identifiers[_identifier_select(spacecraft)]
        
    local_base_dir = stereo_dir / sc_ident / timedirs[timeres]
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
    
    units = OrderedDict([('e_07_14', (u.cm**2*u.s*u.sr*u.MeV)**-1), 
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
    fnames = [sc_ident[0]+dt.strftime("eH%y%b") for dt in rrule(MONTHLY, dtstart=starttime, until=endtime)]
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
        
        thisdata = pd.read_table(file, names=names, delim_whitespace=True, header=endline)
        year = thisdata['Year0'][0]
        month = datetime.strptime(thisdata['Month0'][0], '%b').month
        day_list = list(thisdata['day0'])
        hour0, min0 = divmod(thisdata['hour0minute0'], 100)
        hour1, min1 = divmod(thisdata['hour1minute1'], 100)
        # Get minutes at the midpoint of the bin
        day0list = [d+h/24. +m/1440. for (d, h, m) in zip(thisdata['day0'], hour0, min0)]
        day1list = [d+h/24. +m/1440. for (d, h, m) in zip(thisdata['day1'], hour1, min1)]
        len_ = len(thisdata)
        time_index = convert_datetime(year, month, day0list, day1list, len_)
        thisdata['Time'] = pd.to_datetime(time_index)
        thisdata = thisdata.set_index('Time')
        thisdata = thisdata.drop(["Verse", "Year0", "Month0", "day0", "hour0minute0", 
                                 "Year1", "Month1", "day1", "hour1minute1"], axis=1)
        return thisdata

    def convert_datetime(year, month, day0list, day1list, len_):
        datetime_index = []
        base_date = datetime(year, month, 1, 0, 0, 0)
        for x in range(0, len_):
            time0delta = timedelta(days=day0list[x])
            time1delta = timedelta(days=day1list[x])
            time_delta = (time0delta+time1delta)/2
            datetime_index.append(base_date + time_delta)
        return datetime_index

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)
