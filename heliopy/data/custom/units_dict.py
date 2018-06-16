import astropy.units as u
from collections import OrderedDict


def get(unit_string):
    units = OrderedDict([('ratio', u.dimensionless_unscaled),
                        ('#/cc', u.cm**-3),
                        ('#/cm^3', u.cm**-3),
                        ('cm^{-3}', u.cm**-3),
                        ('ionic charge', u.electron),
                        ('earth radii', u.earthRad),
                        ('Re', u.earthRad),
                        ('Degrees', u.deg),
                        ('degrees', u.deg),
                        ('#/{cc*(cm/s)^3}', (u.cm**3 * (u.cm / u.s)**3)**-1),
                        ('Angle', u.deg),
                        ('sec', u.s),
                        ('nT GSE', u.nT),
                        ('nT GSM', u.nT),
                        ('nT DSL', u.nT),
                        ('msec', u.ms),
                        ('nT SSL', u.nT)])
    try:
        return units[unit_string]
    except KeyError:
        return None
