"""
Methods for working out various quanties of interest to plasmas.

Note that units are in general not SI. The following units are used throughout:

* Number density: cm^-3
* Mangetic field: nT
* Mass: kg
* Pressure: Pa
* Temperature: Kelvin
* Velocity: km/s
"""
import numpy as np
from heliopy import constants


def alfvenspeed(n, B):
    """
    Given number density and magnetic field strength, return Alfven speed

    Parameters
    ----------
    n : array_like
        Number density in cm^-3
    B : array_like
        Magnetic field magnitude in nT

    Returns
    -------
    v_a : array_like
        Alfven speed in km/s
    """
    n *= 1e6
    B *= 1e-9
    v_a = B / np.sqrt(constants.mu_0 * constants.m_p * n)
    v_a *= 1e-3
    return v_a


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
        Temperatures in Kelvin.
    """
    v *= 1e3
    t = m * v**2 / constants.k_B
    return t


def magneticpressure(B):
    """
    Returns magnetic pressure given magnetic field magnitude

    Parameters
    ----------
    B : array_like
        Magnetic field magnitude in nT

    Returns
    -------
    p : array_like
        Pressure in Pascals
    """
    # Convert to Tesla
    B *= 1e-9
    p = B**2 / (2 * constants.mu_0)
    return p
