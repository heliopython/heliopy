"""Methods for working with spectra."""
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

import heliopy.stats as heliostats


def spectral_slopes(fs, power, nbins=10, spacing='linear'):
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
        nbins : int
            Number of bins to split slope calculation into.
        spacing : string
            Either 'linear' or 'log'
    """
    # Sort frequencies
    argsorted = np.argsort(fs)
    fs = fs[argsorted]
    power = power[argsorted]

    # Calculate bin size
    if spacing == 'linear':
        bins = np.linspace(fs[0], fs[-1], nbins + 1)
    elif spacing == 'log':
        bins = np.logspace(np.log10(fs[0]), np.log10(fs[-1]), nbins + 1)
    else:
        raise RuntimeError('spacing argument must be either "linear" or "log"')

    # Perform linear regression in logspace
    out = heliostats.binfunc(np.log10(fs),
                             np.log10(power),
                             np.log10(bins),
                             linregress)
    out = np.array(out)
    # Extract slopes and their errors
    slopes = out[:, 0]
    stderr = out[:, 4]

    return np.array(bins), slopes, stderr
