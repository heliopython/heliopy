"""Methods for working with spectra."""
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

import heliopy.stats as heliostats


def spectral_slopes(fs, power, nbins=10):
    """
    Calculates the slope of a power spectra in bins.

    The bins are spaced linearly from the lowest frequency up. The last bin
    will contain fewer points than the preceding bins.


    Parameters
    ----------
        fs : array_like
            Frequencies.
        power : array_like
            Power at corresponding frequencies.
        nbins : int
            Number of bins to split slope calculation into.
    """
    # Sort frequencies
    argsorted = np.argsort(fs)
    fs = fs[argsorted]
    power = power[argsorted]

    # Calculate bin size
    binsize = int(np.floor(fs.size / nbins))
    # Create list of bins
    bins = []
    for i in range(0, nbins):
        bins.append(fs[i * binsize])
    bins.append(fs[-1])

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
