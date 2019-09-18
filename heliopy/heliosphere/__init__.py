import astropy.units as u


class ParkerSpiral:
    r"""
    A Parker spiral mangetic field line.

    Parameters
    ----------
    v : ~astropy.units.Quantity
        Solar wind speed.
    r0 : ~astropy.units.Quantity
        Radial distance from the solar center of a reference point on
        the spiral.
    l0 : ~astropy.units.Quantity
        Longitude of the reference point on the spiral.

    Notes
    -----
    The longitude of the spiral as a funciton of r is given by

    .. math::

        \phi = \phi_{0} - \Omega_{\odot} \left ( r - r_{0} \right ) / v_{sw}

    where :math:`\phi_{0}` and :math:`r_{0}` are a reference longitude and
    radial distance that the spiral passes through, :math:`\Omega_{\odot}`
    is the solar rotation rate, :math:`v_{sw}` is the solar wind speed,
    and :math:`r` is the radial distance from the solar center.
    """
    def __init__(self, v, r0, l0):
        self.v = v
        self.r0 = r0
        self.l0 = l0

    def longitude(self, rs):
        """
        Sample the spiral longitude at given radial distances.

        Parameters
        ----------
        rs : ~astropy.units.Quantity
            Radial distance(s).
        """
        omega_sun = 14.713 * (u.deg / u.day)
        return (self.l0 - (omega_sun * (rs - self.r0) / self.vsw)).to(u.deg)
