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
    allowed = ['STA', 'STB']
    if sc.upper() not in allowed:
        raise ValueError(f'spacecraft value "{sc}" not in list of '
                         f'allowed values "{allowed}"')
    return sc.upper()


def _stereo(starttime, endtime, spacecraft, identifier, dataset='ac',
            units=None, warn_missing_units=True):
    """
    Generic method for downloading STEREO data.
    """

    directory = pathlib.Path("stereo", _identifier_select(spacecraft))
    badvalues = 1e-31
    return cdasrest.CDASDwonloader(dataset, identifier, directory,
                                   badvalues=badvalues,
                                   warn_missing_units=warn_missing_units,
                                   units=units)


def mag_l1_rtn(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft) + '_L1_MAG_RTN'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled),
                        ('MAGFLAGUC', u.dimensionless_unscaled)])
    dl = _stereo(starttime, endtime, spacecraft, identifier, units=units)
    return dl.load(starttime, endtime)


mag_l1_rtn.__doc__ = _docstring('STA_L1_MAG_RTN',
                                'STEREO IMPACT/MAG Magnetic Field Vectors.')


def magplasma_l2(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft) + '_L2_MAGPLASMA_1M'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    dl = _stereo(starttime, endtime, spacecraft, identifier, units=units)
    return dl.load(starttime, endtime)


magplasma_l2.__doc__ = _docstring(
    'STA_L2_MAGPLASMA_1M',
    'STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data.')
