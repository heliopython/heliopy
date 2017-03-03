"""Methods for working with spectra."""
import numpy as np
from scipy.stats import linregress

import heliopy.stats.stats as heliostats


def spectral_slopes(fs, power, bins=10, spacing='linear'):
    """
    Calculates the local power law of a specturm across multiple bins.

    The bins are equally spaced from the lowest provided frequency to the
    highest frequency. Data in each bin is then fitted with a straight line in
    log space to estimate the local power law.


    Parameters
    ----------
    fs : array_like
        Frequencies.
    power : array_like
        Power at corresponding frequencies.
    bins : int or sequence of scalars, default: 10
        If an integer, number of bins to calculate slopes over.
        If a sequence of scalars, the sequence defines the edges of the
        frequency bins in which to calculate the slopes.
    spacing : string, default: 'linear'
        If *bins* is an integer, the method of spacing frequency bins.
        Either 'linear' or 'log'.

    Returns
    -------
    bins : array_like
        Bins in which each power law is fitted
    slopes : array_like
        Estimates for the power law indices
    stderr : array_like
        Estimate of the standard error in fitting a straight line to the data
        in log space
    """
    # Sort frequencies
    argsorted = np.argsort(fs)
    fs = fs[argsorted]
    power = power[argsorted]
    if fs[0] == 0:
        fs = fs[1:]
        power = power[1:]

    # Calculate bin size
    if isinstance(bins, int):
        if spacing == 'linear':
            bins = np.linspace(fs[0], fs[-1], bins + 1)
        elif spacing == 'log':
            bins = np.logspace(np.log10(fs[0]), np.log10(fs[-1]), bins + 1)
        else:
            raise RuntimeError('spacing argument must be either "linear" '
                               'or "log"')

    # Perform linear regression in logspace
    out = heliostats.binfunc(np.log10(fs),
                             np.log10(power),
                             np.log10(bins),
                             linregress)
    out = np.array(out)
    # Extract slopes and their errors
    slopes = out[:, 0]
    stderr = out[:, 4]
    slopes[np.isnan(stderr)] *= np.nan

    return np.array(bins), slopes, stderr
