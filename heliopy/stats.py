"""Statistical methods"""
import numpy as np


def hist(x, bins='auto', normed=True, return_centres=True):
    """
    Improved histogram function

    Parameters
    ----------
        x : array_like
            Data values.
        bins : int | string
            Number of bins in output.
        normed : bool
            If true, return a normalised histogram such that the sum of values
            in each bin times the bin width is 1.
        return_centres : bool
            If True, returns the co-ordinates of the bin centres. If False,
            returns the co-ordinates of the bin edges.

    Returns
    -------
        hist : array_like
            Histogram values.
        bins : array_like
            Bin centres or bin edges (depends on value of return_centres
            argument)
    """
    hist, bin_edges = np.histogram(x, bins=bins, normed=normed)
    # Calculate centres of bins (e.g. for plotting scatter pdf)
    bin_centres = (bin_edges[1:] + bin_edges[:-1]) / 2
    if return_centres:
        return hist, bin_centres
    else:
        return hist, bin_edges


def binmean(x, y, bins):
    """
    Returns the mean of data points lying in given bins.

    Parameters
    ----------
        x : array_like
            x co-ordinates of data points.
        y : array_like
            data points
        bins : array_like
            Bin edges.

    Returns
    -------
        means : array_like
            The mean of y values in each bin. If no data points are present in
            a bin, the mean value is set to nan. Size is bins.size - 1.
    """
    means = np.zeros(bins.size - 1) * np.nan
    for i in range(0, bins.size):
        left = bins[i]
        right = bins[i + 1]
        tokeep = np.logical_and(x > left, x < right)
        means[i] = np.mean(x[tokeep])
    return means
