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
    T : array_like
        Temperatures in Kelvin.
    """
    v *= 1e3
    T = m * v**2 / (2 * constants.k_B)
    return T


def temp2vth(T, m):
    """
    Converts temperature to thermal speed.

    Parameters
    ----------
    T : array_like
        Temperatures in Kelvin.
    m : float
        Particle mass in kg.

    Returns
    -------
    v : array_like
        Thermal velocities in km/s.
    """
    v = np.sqrt(2 * T * constants.k_B / m)
    return v / 1e3


def p_mag(B):
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
    B = B * 1e-9
    return B**2 / (2 * constants.mu_0)


def p_th(n, T):
    """
    Returns thermal pressure given number density and temperature.

    Parameters
    ----------
    n : array_like
        Number density in cm^-3
    T : array_like
        Temperature in Kelvin

    Returns
    -------
    p : array_like
        Pressure in Pascals
    """
    # Convert to m^-3
    n = n * 1e6
    return n * constants.k_B * T
