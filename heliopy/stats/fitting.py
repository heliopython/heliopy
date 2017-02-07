"""Methods to fit statistical distributions to data"""
import numpy as np


def bin_2d_data(x, y, normed=True):
    """
    Bin a 2D data set

    Parameters
    ----------
    x : array_like
        x data points
    y : array_like
        y data points
    normed : bool, optional
        If ``True``, normalise output histogram, otherwise return counts in
        each bin. Default is ``False``.

    Returns
    -------
    hist : 2D array_like
        Histogram of binned data
    xedges : 1D array_like
        Edges of the x bins
    yedges : 1D array_like
        Edges of the y bins
    xbins : 2D array_like
        x coordiantes of the data points in *hist*
    ybins : 2D array_like
        y coordinates of the data points in *hist*
    """
    hist, xedges, yedges = np.histogram2d(x, y, bins=100, normed=True)
    # Transpose due to a inconsitensy with histogram2d and meshgrid
    hist = hist.T
    xbins = (xedges[1:] + xedges[:-1]) / 2
    ybins = (yedges[1:] + yedges[:-1]) / 2
    xbins, ybins = np.meshgrid(xbins, ybins)
    return hist, xedges, yedges, xbins, ybins


def fit_2d_residuals(x, y, f, *fargs):
    """
    Return the residuals from a fitted distribution

    The input data is binned using :func:`bin_2d_data`, and the distribution
    given by ``f(x, y, *fargs)`` evaluated at each bin. The fitted function is
    then subtracted from the binned data to give the residuals.

    Parameters
    ----------
    x : array_like
        x data values
    y : array_like
        y data values
    f : callable
        Function fitted to data. *f* must take *x* and *y* as its first two
        arguments, and then the fit parameters (*fargs*) as the remaining
        arguments

    Returns
    -------
    resids : array_like
        The residuals at each (*x*, *y*) coordinate
    """
    hist, _, _, xbins, ybins = bin_2d_data(x, y)
    hist_fit = f(xbins, ybins, *fargs)
    return hist - hist_fit


def fit_2d(x, y, f, x0, **minkwargs):
    """
    Fit a function to a 2D data set

    The function is fitted by minimising the sum of the aboslute values of
    the residuals calculated using :func:`fit_2d_residuals`.

    Parameters
    ----------
    x : array_like
        x data values
    y : array_like
        y data values
    f : callable
        Function fitted to data. *f* must take *x* and *y* as its first two
        arguments, and then the fit parameters as the remaining
        arguments
    x0 : tuple
        Initial guess for the fit parameters. ``len(x0)`` must equal the number
        of additional paramerts that *f* takes.
    minkwargs
        Keyword arguments are passed to `minimize`

    Returns
    -------
    resids : array_like
        The residuals at each (*x*, *y*) coordinate
    """
    def resids(args):
        r = fit_residuals(x, y, f, *args)
        return np.sum(np.abs(r))

    return opt.minimize(resids, x0, **minkwargs)
