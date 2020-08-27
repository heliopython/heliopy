"""
Methods for importing data from the STEREO spacecraft.
"""
from collections import OrderedDict
import pathlib
import astropy.units as u
from heliopy.data import cdasrest


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
    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled),
                        ('MAGFLAGUC', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, 'L1_MAG_RTN', units=units)


mag_l1_rtn.__doc__ = _docstring('STA_L1_MAG_RTN',
                                'STEREO IMPACT/MAG Magnetic Field Vectors.')


def magplasma_l2(spacecraft, starttime, endtime):
    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, 'L2_MAGPLASMA_1M',
                   units=units, intervals='monthly')


magplasma_l2.__doc__ = _docstring(
    'STA_L2_MAGPLASMA_1M',
    'STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data.')
