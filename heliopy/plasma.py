"""
Methods for working out various quanties of interest to plasmas
"""
from heliopy import constants


def vth2temp(v, m):
    """
    Converts thermal velocity to temperature.

    Parameters
    ----------
        v : array_like
            Thermal velocities in km/s.
        m : float
            Particle mass in kg.

    Returns
    -------
        t : array_like
            Temperatures.
    """
    v *= 1e3
    t = m * v**2 / constants.k_B
    return t


def magneticpressure(B):
    """
    Returns magnetic pressure given magnetic field magnitude.

    Parameters
    ----------
        B : array_like
            Magnetic field magnitude in nT.

    Returns
    -------
        p : array_like
            Pressure in Pascals.
    """
    # Convert to Tesla
    B *= 1e-9
    p = B**2 / (2 * constants.mu_0)
    return p
