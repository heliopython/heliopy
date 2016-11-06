"""
Methods for working out various quanties of interest to plasmas
"""
from heliopy import constants


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
