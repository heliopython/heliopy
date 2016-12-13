"""Methods for working with the sun."""
import numpy as np


def rotationrate(lat):
    """
    Return the rotation rate of the sun as a function of solar lattitude.

    Equation is (4) from http://iopscience.iop.org/article/10.1088/1742-6596/118/1/012029/pdf

    Parameters
    ----------
        lat : array_like
            Lattitude in radians. 0 is the equator, postive values are towards
            the north pole.

    Returns
    -------
        rot_rate : array_like
            Rotation rate in radians / second.
    """
    assert np.all(np.abs(lat) <= np.pi / 2)
    # Rotation rate in degrees / day
    rot_rate_days = 14.050 - (1.492 * np.sin(lat)**2) - (2.606 * np.sin(lat)**4)
    rot_rate = np.deg2rad(rot_rate_days) / (24 * 60 * 60)
    return rot_rate
