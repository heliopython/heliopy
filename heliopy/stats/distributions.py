"""Statisitcal models"""
import numpy as np
import heliopy.vector.transformations as transformations


def maxwellian_1D(v, n, v0, vth):
    r"""
    1D Maxwell-Boltzmann velocity distribution, defined as
    :math:`f \left (v \right ) = 4 * \pi $ v^{2} n \left ( \frac{1}{\pi v_{th}} \right )^{\frac{3}{2}} e^{-v^{2} / v_{th}^{2}}`

    Parameters
    ----------
    v : array_like
        Velocity values
    n : float
        Amplitude of the distribution. Often interpreted as a number density.
    vth : float
        Thermal speed of the distribution

    Returns
    -------
    pdf : array_like
        pdf at the given velocity values

    References
    ----------
    'Basic space plasma physics' by Baumjohann and Treumann, section 6.3
    """
    prefactor = n * 4 * np.pi * v**2 * np.power(1 / (np.pi * vth), 1.5)
    return prefactor * np.exp(-((v - v0) / vth)**2)


def kent_dist(theta, phi, kappa, beta, theta_0, phi_0, theta_1, phi_1):
    """
    An asymmetric distribution on a sphere, centred on a single point.

    *theta_0* and *phi_0* give the co-ordinates of the distribution peak at
    :math:`r_{0}`. *theta_1* and *phi_1* (relative to :math:`r_{0}`) give the
    direction of the maximum width of the distribution.

    Parameters
    ----------
    theta : array_like
        theta values, defined in the range :math:`[-\pi / 2, \pi / 2]`
    phi : array_like
        phi values, defined in the range :math:`[-\pi, \pi]`
    kappa : float
        The 'width' of the distribution in the :math:`r_{0}` direction.
        The larger kappa is, the wider the distribution in this direction.
    beta : float
        The 'width' of the distribution in the direction perpendicular to
        :math:`r_{0}` and :math:`r_{1}`. The larger beta is, the wider the
        distribution in this
        direction.
    theta_0 : float
        The theta co-ordinate of the distribution peak
    phi_0 : float
        The phi co-ordinate of the distribution peak
    theta_0 : float
        The theta co-ordinate of the direciton of the distribution maximum
        width
    phi_1 : float
        The phi co-ordinate of the direciton of the distribution maximum
        width

    Returns
    -------
    pdf : array_like
        The probability density at the given (theta, phi) coordinates

    Notes
    -----
    The distribution returned by this method is not normalised. The
    `normalise_kent` method can be used to numerically normalise a Kent
    distribution.

    References
    ----------
    'Statistical analysis of spherical data' by Fisher, Lewis, Embleton,
    section 4.4.5
    """
    assert kappa > 2 * beta,\
        'kappa must be > 2 * beta for a unimodal distribution'

    def get_cart(theta, phi):
        return np.array(transformations.sph2cart(1, theta, phi))
    r_0 = get_cart(theta_0, phi_0)
    r_1 = get_cart(theta_1, phi_1)
    # Get directon perpendicular to peak and maximum width direction
    r_2 = np.cross(r_1, r_0)
    r_1_new = np.cross(r_0, r_2)
    assert np.dot(r_1_new, r_1) > 0
    r_1 = r_1_new

    def normalise(v):
        return v / np.linalg.norm(v)
    r_1 = normalise(r_1)
    r_2 = normalise(r_2)

    r = np.dstack(transformations.sph2cart(1, theta, phi))

    # Work out weight for these parameters
    weight = kappa * (np.dot(r, r_0))
    weight += beta * (np.dot(r, r_1)**2 - np.dot(r, r_2)**2)
    return np.exp(weight) * np.cos(theta)


def fisher_dist(theta, phi, kappa, theta_0, phi_0):
    """
    A symmetric distribution on a sphere, centred on a single point.

    Parameters
    ----------
    theta : array_like
        theta values, defined in the range :math:`[-\pi / 2, \pi / 2]`
    phi : array_like
        phi values, defined in the range :math:`[-\pi, \pi]`
    kappa : float
        The 'width' of the distribution. The larger kappa is, the wider the
        distribution
    theta_0 : float
        The theta co-ordinate of the distribution centre
    phi_0 : float
        The phi co-ordinate of the distribution centre

    Returns
    -------
    pdf : array_like
        The probability density at the given (theta, phi) coordinates

    References
    ----------
    'Statistical analysis of spherical data' by Fisher, Lewis, Embleton,
    section 4.4.3

    Examples
    --------
    Fisher distributions with different widths:

    .. literalinclude:: /scripts/fisher_dist.py
    .. image:: /figures/fisher_dist.png
    """
    C = kappa / (4 * np.pi * np.sinh(kappa))
    exp = np.exp(kappa *
                 (np.cos(theta) * np.cos(theta_0) * np.cos(phi - phi_0) +
                  (np.sin(theta) * np.sin(theta_0))))
    return C * exp * np.cos(theta)
