"""
Methods for importing data from the STEREO spacecraft.
"""
import astropy.units as u
from heliopy.data import cdasrest


def _check_spacecraft(sc):
    allowed = ['A', 'B']
    if sc.upper() not in ['A', 'B']:
        raise ValueError(f'spacecraft value "{sc}" not in list of '
                         f'allowed values "{allowed}"')


def _docstring(identifier, description):
    ds = f"""
    {description} data.

    See https://cdaweb.sci.gsfc.nasa.gov/misc/NotesS.html#STA_{identifier}
    for more information.

    Parameters
    ----------
    spacecraft : str
        Spacecraft letter, one of ``['A', 'B']``.
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
    """
    return ds


def _stereo(starttime, endtime, spacecraft, identifier, units=None,
            intervals='monthly'):
    """
    Generic method for downloading STEREO data.
    """
    _check_spacecraft(spacecraft)
    dataset = 'st' + spacecraft.lower()
    identifier = 'ST' + spacecraft.upper() + '_' + identifier
    dl = cdasrest.CDASDwonloader(dataset, identifier, 'stereo', units=units)
    # Override intervals
    if intervals == 'daily':
        dl.intervals = dl.intervals_daily
    else:
        dl.intervals = dl.intervals_monthly
    return dl.load(starttime, endtime)


# Actual download functions start here
def coho1hr_merged(spacecraft, starttime, endtime):
    identifier = 'COHO1HR_MERGED_MAG_PLASMA'
    return _stereo(starttime, endtime, spacecraft, identifier)


coho1hr_merged.__doc__ = _docstring(
    'COHO1HR_MERGED_MAG_PLASMA',
    'Merged hourly magnetic field, plasma, proton fluxes, and ephermis')
