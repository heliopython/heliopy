"""
Methods for retrieving the location of Earth.
"""
from datetime import datetime
import pandas as pd
import numpy as np


def clong(time):
    """
    Returns the Carrington Longitude of a given datetime.

    Parameters
    ----------
    time : datetime
        Input time

    Returns
    -------
    lon : float
        Carrington longitude in radians
    """
    ref_time = datetime(1854, 1, 1, 12, 0, 0)
    rot_period = 25.38 * 24 * 60 * 60
    dt = time - ref_time
    if type(dt) == pd.Series:
        dt = dt.dt
    lon = -(dt.total_seconds() / rot_period) * 2 * np.pi
    return np.mod(lon, 2 * np.pi)
