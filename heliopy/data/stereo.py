"""
Methods for importing data from the STEREO spacecraft.
"""
from collections import OrderedDict
import pathlib
import astropy.units as u
from heliopy.data import cdasrest
from heliopy.data import util


def _docstring(identifier, description):
    ds = f"""
    {description}

    See https://cdaweb.sci.gsfc.nasa.gov/misc/NotesS.html#{identifier}
    for more information.

    Parameters
    ----------
    spacecraft : str
        Spacecraft identifier, one of ``['STA', 'STB']``.
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
    """
    return ds


def _identifier_select(sc):
    """
    Spacecraft selector for STEREO.
    """
    sc = sc.upper()
    allowed = ['STA', 'STB', 'A', 'B']
    if sc not in allowed:
        raise ValueError(f'spacecraft value "{sc}" not in list of '
                         f'allowed values "{allowed}"')
    if sc in ['A', 'B']:
        sc = f'ST{sc}'
    return sc


def _stereo(starttime, endtime, spacecraft, identifier,
            intervals='daily', units=None, warn_missing_units=True):
    """
    Generic method for downloading STEREO data.
    """
    spacecraft = _identifier_select(spacecraft)

    dataset = spacecraft.lower()
    identifier = spacecraft.upper() + '_' + identifier
    dl = cdasrest.CDASDwonloader(dataset, identifier, 'stereo', units=units)

    if intervals == 'monthly':
        dl.intervals = dl.intervals_monthly
    else:
        dl.intervals = dl.intervals_daily
    return dl.load(starttime, endtime)


# Actual download functions start here
def coho1hr_merged(spacecraft, starttime, endtime):
    return _stereo(starttime, endtime, spacecraft, 'COHO1HR_MERGED_MAG_PLASMA',
                   intervals='monthly')


coho1hr_merged.__doc__ = _docstring(
    'COHO1HR_MERGED_MAG_PLASMA',
    'Merged hourly magnetic field, plasma, proton fluxes, and ephermis')


def mag_l1_rtn(spacecraft, starttime, endtime):
    units = OrderedDict([('MAGFLAGUC', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, 'L1_MAG_RTN', units=units)


mag_l1_rtn.__doc__ = _docstring('STA_L1_MAG_RTN',
                                'STEREO IMPACT/MAG Magnetic Field Vectors.')


def magplasma_l2(spacecraft, starttime, endtime):
    return _stereo(starttime, endtime, spacecraft, 'L2_MAGPLASMA_1M',
                   intervals='monthly')


magplasma_l2.__doc__ = _docstring(
    'STA_L2_MAGPLASMA_1M',
    'STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data.')


def let_l1(spacecraft, starttime, endtime):
    return _stereo(starttime, endtime, spacecraft, 'L1_LET')


let_l1.__doc__ = _docstring('STA_L1_LET',
                            """STEREO IMPACT/LET Level 1 Data

    Note that the energies are given in units MeV/n and the 
    intensities in units (1/(cm^2 s sr MeV/nuc)). The astropy
    units cannot consistently give a unit per nucleon""")


def sept_l1(spacecraft, starttime, endtime):
    units = OrderedDict([('Heater_NS', u.deg_C),
                         ('Heater_E', u.deg_C)])
    sept = _stereo(starttime, endtime, spacecraft, 'L1_SEPT', units=units)
    data = sept.to_dataframe()
    data['Epoch_NS'] = util.epoch_to_datetime(data['Epoch_NS'].values)
    data['Epoch_E'] = util.epoch_to_datetime(data['Epoch_E'].values)

    return util.units_attach(data, sept.units)


sept_l1.__doc__ = _docstring('STA_L1_SEPT',
                             'STEREO IMPACT/SEPT Level 1 Data')


def sit_l1(spacecraft, starttime, endtime):
    return _stereo(starttime, endtime, spacecraft, 'L1_SIT')


sit_l1.__doc__ = _docstring('STA_L1_SIT',
                            """STEREO IMPACT/SIT Level 1 Data

    Note that the energies are given in units MeV/n and the 
    intensities in units (1/(cm^2 s sr MeV/nuc)). The astropy
    units cannot consistently give a unit per nucleon""")
