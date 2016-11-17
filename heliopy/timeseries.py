"""Methods for processing time series data"""
from datetime import datetime, time, timedelta
import numpy as np


def removespikes(v, threshold):
    """
    Replace spikes in data with nans. Spikes are indentified as follows:
    * The discrete second derivative is calculated at each point.
    * The standard deviation of all the second derivatives is taken (std).
    * All points whose second derivative magnitude is greater than threshold *
    std are replace with nans.

    Parameters
    ----------
        v : array_like
            Data to remove spikes from.
        threshold : float
            Treshold to determine size of spikes to remove.

    Returns
    -------
        out : array_like
            De-spiked data.
    """
    # Discrete second derivative
    diffs = np.absolute(np.diff(v[1:]) - np.diff(v[:-1]))
    sigma_diffs = np.std(diffs)
    threshold = threshold * sigma_diffs
    diffs = np.concatenate(([0], diffs, [0]))
    toremove = np.logical_or(diffs < -threshold, diffs > threshold)
    out = v.copy()
    out[toremove] *= np.nan

    return out
