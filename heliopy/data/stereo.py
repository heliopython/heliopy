"""
Methods for importing data from the STEREO spacecraft.

Most data is publically available at https://cdaweb.gsfc.nasa.gov/index.html/.

The STEREO spacecraft homepage can be found at https://stereo.gsfc.nasa.gov/.

The particle instrument data is available at http://www.srl.caltech.edu/STEREO/
Please refer to the documentation of the data found there.

In particular read the instrument and data notes and caveats!
"""
from collections import OrderedDict
import pathlib
from datetime import datetime, timedelta
from dateutil.rrule import rrule, MONTHLY, DAILY

import astropy.units as u
import astropy.time
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
                            """STEREO IMPACT/LET Level 1 Data

    Note that the energies are given in units MeV/n and the 
    intensities in units (1/(cm^2 s sr MeV/nuc)). The astropy
    units cannot consistently give a unit per nucleon""")


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
                            """STEREO IMPACT/SIT Level 1 Data

    Note that the energies are given in units MeV/n and the 
    intensities in units (1/(cm^2 s sr MeV/nuc)). The astropy
    units cannot consistently give a unit per nucleon""")


# +
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
        
    local_base_dir = stereo_het_l2_dir / identifier / (identifier+"_L1_HET") / timedirs[timeres]
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

    units = OrderedDict([('Time', u.ms),
                         ('Epoch0', u.ms),
                         ('Epoch1', u.ms),
                         ('Verse', u.dimensionless_unscaled),
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
        thisdata['Epoch0'] = t0
        if timeres != "1m":
            thisdata['Epoch1'] = t1
            thisdata = thisdata.drop(["Year1", "Month1", "day1", "hour1minute1"], axis=1)

        thisdata = thisdata.drop(["Verse", "Year0", "Month0", "day0", "hour0minute0"], axis=1)
        thisdata = thisdata.set_index('Time')
        return thisdata

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)


def sept_l2(starttime, endtime, spacecraft, species, view, timeres):
    """
    Import STEREO SEPT level 2 data.

    Data documentation is available at
    
    http://www2.physik.uni-kiel.de/stereo/index.php?doc=data
    
    Please note that the Time corresponds to the centre of the time bin.

    Parameters
    ----------
        starttime : datetime
            Interval start time.
        endtime : datetime
            Interval end time.
        spacecraft: string
            Either "sta" or "stb"
        species: string
            Either "e" or "i", for electrons and ions
        view: string
            viewing direction: "sun", "asun", "north", "south" or "omni"
        timeres: string
            Valid values are "1m", "10m", "1h", "1d"
            
    Returns
    -------
        data : :class:`~sunpy.timeseries.TimeSeries`
    """
    
    sept_l2_url = 'http://www2.physik.uni-kiel.de/stereo/data/sept/level2'
    
    data_dir = pathlib.Path(config['download_dir'])
    
    stereo_sept_l2_dir = data_dir / 'stereo'

    if timeres not in ("1m", "10m", "1h", "1d"):
        raise ValueError("Invalid time resolution, should be 1m, 10m, 1h or 1d")

    timedirs = {"1m": "1min",
              "10m": "10min",
              "1h": "1h", 
              "1d": "1d"}
    
    sc_identifiers = {"STA": "ahead",
                        "STB": "behind"}
    
    identifier = _identifier_select(spacecraft)
    sc_ident = sc_identifiers[identifier]
    speciesident = "ele" if species=="e" else "ion"
        
    local_base_dir = stereo_sept_l2_dir / identifier / (identifier+"_L2_SEPT")
    remote_base_url = sept_l2_url

    if species == 'e':
        names = ['Julian', 'Year', 'Doy',
                'hour', 'minute', 'second',
                'e_45_55', 'e_55_65', 'e_65_75',
                'e_75_85', 'e_85_105', 'e_105_125',
                'e_125_145', 'e_145_165', 'e_165_195',
                'e_195_225', 'e_225_255', 'e_255_295',
                'e_295_335', 'e_335_375', 'e_375_425',
                'e_45_55_unc', 'e_55_65_unc', 'e_65_75_unc',
                'e_75_85_unc', 'e_85_105_unc', 'e_105_125_unc',
                'e_125_145_unc', 'e_145_165_unc', 'e_165_195_unc',
                'e_195_225_unc', 'e_225_255_unc', 'e_255_295_unc',
                'e_295_335_unc', 'e_335_375_unc', 'e_375_425_unc',
                'dt']
        units = OrderedDict()
        for n in names[:6]:
            units.update({n:u.dimensionless_unscaled})
        for n in names[6:21]:
            units.update({n:(u.cm**2*u.s*u.sr*u.MeV)**-1})
        for n in names[21:-1]:
            units.update({n:u.dimensionless_unscaled})
        units.update({names[-1]:u.s})
    elif species == 'i':
        names = ['Julian', 'Year', 'Doy',
                'hour', 'minute', 'second',
                'i_84_92', 'i_92_101', 'i_101_110',
                'i_110_118', 'i_118_137', 'i_137_155',
                'i_155_174', 'i_174_192', 'i_192_219',
                'i_219_246', 'i_246_273', 'i_273_312',
                'i_312_350', 'i_350_389', 'i_389_438',
                'i_438_496', 'i_496_554', 'i_554_622',
                'i_622_700', 'i_700_788', 'i_788_875',
                'i_875_982', 'i_982_1111', 'i_1111_1250',
                'i_1250_1399', 'i_1399_1578', 'i_1578_1767',
                'i_1767_1985', 'i_1985_2223', 'i_2223_6500',
                'i_84_92_unc', 'i_92_101_unc', 'i_101_110_unc',
                'i_110_118_unc', 'i_118_137_unc', 'i_137_155_unc',
                'i_155_174_unc', 'i_174_192_unc', 'i_192_219_unc',
                'i_219_246_unc', 'i_246_273_unc', 'i_273_312_unc',
                'i_312_350_unc', 'i_350_389_unc', 'i_389_438_unc',
                'i_438_496_unc', 'i_496_554_unc', 'i_554_622_unc',
                'i_622_700_unc', 'i_700_788_unc', 'i_788_875_unc',
                'i_875_982_unc', 'i_982_1111_unc', 'i_1111_1250_unc',
                'i_1250_1399_unc', 'i_1399_1578_unc', 'i_1578_1767_unc',
                'i_1767_1985_unc', 'i_1985_2223_unc', 'i_2223_6500_unc',
                'dt']
        units = OrderedDict()
        for n in names[:6]:
            units.update({n:u.dimensionless_unscaled})
        for n in names[6:36]:
            units.update({n:(u.cm**2*u.s*u.sr*u.MeV)**-1})
        for n in names[36:-1]:
            units.update({n:u.dimensionless_unscaled})
        units.update({names[-1]:u.s})        
    else:
        raise ValueError("Invalid species, should be 'e' or 'i'")
        
    extension = ".dat"
    # Create monthly filenames
    sttime = datetime(starttime.year, starttime.month, starttime.day)
    fnames = ["sept_"+sc_ident+"_"+speciesident+"_"+view+"_"+dt.strftime("%Y")+
              "_"+dt.strftime("%j")+"_"+timedirs[timeres]+"_l2_v03" 
              for dt in rrule(DAILY, dtstart=sttime, until=endtime)]
    
    dirs = [pathlib.Path(sc_ident) / timedirs[timeres] / dt.strftime("%Y") 
            for dt in rrule(DAILY, dtstart=sttime, until=endtime)]
    
    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        url = f"{remote_base_url}/{directory}"
        util._download_remote(url,
                              fname + extension,
                              local_base_dir / directory)
    
    def processing_func(file):

        # Find end of header
        lines = file.readlines()
        endline = [i for i,l in enumerate(lines) if l=="#BEGIN DATA\n"][0]
        file.seek(0)
        
        thisdata = pd.read_table(file, names=names, delim_whitespace=True, header=endline)
        jdt = astropy.time.Time(thisdata.Julian, format="jd")
        thisdata['Time'] = jdt.to_datetime()

        thisdata = thisdata.set_index('Time')
#         thisdata = thisdata.drop(["Verse", "Year0", "Month0", "day0", "hour0minute0"], axis=1)
#         if timeres != "1m":
#             thisdata = thisdata.drop(["Year1", "Month1", "day1", "hour1minute1"], axis=1)
        return thisdata

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units)
