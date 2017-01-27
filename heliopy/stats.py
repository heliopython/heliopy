"""Statistical methods"""
import numpy as np
import scipy.stats as stats
import inspect


def multi_variate_mode(data, bins=100):
    """
    Calculate the mode of a multi-variable data set.

    A d-dimensional histogram is calculated for the data, and the peak of the
    histogram found. By default the number of bins is 100 in each dimesnion.

    Parameters
    ----------
    data : array_like
        Input data. Different data dimensions are assumed to be columns.
    bins : int
        Number of bins to use when taking the histogram

    Returns
    -------
    mode : array_like
        Mode of the data set. A 1D array with the number of entries equal to
        the number of columns in *data*.
    """
    mode = []
    hist, edges = np.histogramdd(np.array(data),
                                 normed=True,
                                 bins=100)
    peak = np.unravel_index(np.argmax(hist), hist.shape)
    for i, edge in enumerate(edges):
        bins = (edge[:-1] + edge[1:]) / 2
        mode.append(bins[peak[i]])
    return np.array(mode)


def _edges_to_centres(bin_edges):
    """Converts bin edges to bin centres"""
    return (bin_edges[1:] + bin_edges[:-1]) / 2


def hist(x, bins='auto', normed=True, return_centres=True, **kwargs):
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
    hist, bin_edges = np.histogram(x, bins=bins, density=normed, **kwargs)
    if return_centres:
        return hist, _edges_to_centres(bin_edges)
    else:
        return hist, bin_edges


def gaussian_kde(x, bins='auto'):
    """
    Improved gaussian kernel density estimation function.

    See https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html
    for the method upon which this is based.

    Parameters
    ----------
        x : array_like
            Data values.
        bins : array | string
            If a sting, will be passed to np.hist to automatically work out
            bins to use. Otherwise the kernel density estimate is evaluated at
            the values provided.

    Returns
    -------
        kde : array_like
            Kernel density estimates.
        bins : array_like
            Location of evalulated values.
    """
    if isinstance(bins, str):
        _, bins = hist(x, bins=bins)
    kernel = stats.gaussian_kde(x)
    kde = kernel.pdf(bins)
    return kde, bins


def binfunc(x, y, bins, f):
    """
    Returns a function applied to data lying in given bins.

    The data is partitioned in the x direction, and the function applied to y
    values.

    Parameters
    ----------
        x : array_like
            x co-ordinates of data points.
        y : array_like
            Data points.
        bins : array_like
            Bin edges.
        f : function
            Function to apply to data points. If f takes only one argument it
            is passed y. If f takes 2 arguments it is passed x and y in that
            order.

    Returns
    -------
        out : list
            The results function applied in each bin. If no data points are
            present in a bin, the value in that bin is set to an emtpy list.
            Length is bins.size - 1.

    """
    if isinstance(bins, list):
        bins = np.array(bins)

    # Check if function takes 1 or 2 arguments
    sig = inspect.signature(f)
    nargs = len(sig.parameters)
    if not (nargs == 1 or nargs == 2):
        raise RuntimeError('User supplied funciton must take 1 or 2 arguments')

    out = []
    for i in range(0, bins.size - 1):
        left = bins[i]
        right = bins[i + 1]
        tokeep = np.logical_and(x >= left, x < right)
        if tokeep.size == 0:
            out.append([])
        else:
            if nargs == 1:
                out.append(f(y[tokeep]))
            if nargs == 2:
                out.append(f(x[tokeep], y[tokeep]))

    return out


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
    def mean(x):
        return np.mean(x)
    return binfunc(x, y, bins, mean)
