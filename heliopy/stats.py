"""Statistical methods"""
import numpy as np
import scipy.stats as stats
import inspect
import heliopy.vector.transformations as transformations


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


def kent_dist(theta, phi, kappa, beta, theta_0, phi_0, theta_1, phi_1):
    """
    An asymmetric distribution on a sphere, centred on a single point.

    *theta_0* and *phi_0* give the co-ordinates of the distribution peak at
    :math:`r_{0}`. *theta_1* and *phi_1* (relative to :math:`r_{0}`) give the
    direction of the maximum width of the distribution.

    Parameters
    ----------
    theta : array_like
        theta values, defined in the range :math:`[-\pi / 2, \pi / 2]`
    phi : array_like
        phi values, defined in the range :math:`[-\pi, \pi]`
    kappa : float
        The 'width' of the distribution in the :math:`r_{0}` direction.
        The larger kappa is, the wider the distribution in this direction.
    beta : float
        The 'width' of the distribution in the direction perpendicular to
        :math:`r_{0}` and :math:`r_{1}`. The larger beta is, the wider the
        distribution in this
        direction.
    theta_0 : float
        The theta co-ordinate of the distribution peak
    phi_0 : float
        The phi co-ordinate of the distribution peak
    theta_0 : float
        The theta co-ordinate of the direciton of the distribution maximum
        width
    phi_1 : float
        The phi co-ordinate of the direciton of the distribution maximum
        width

    Returns
    -------
    pdf : array_like
        The probability density at the given (theta, phi) coordinates

    Notes
    -----
    The distribution returned by this method is not normalised. The
    `normalise_kent` method can be used to numerically normalise a Kent
    distribution.

    References
    ----------
    'Statistical analysis of spherical data' by Fisher, Lewis, Embleton,
    section 4.4.5
    """
    assert kappa > 2 * beta,\
        'kappa must be > 2 * beta for a unimodal distribution'

    def get_cart(theta, phi):
        return np.array(transformations.sph2cart(1, theta, phi))
    r_0 = get_cart(theta_0, phi_0)
    r_1 = get_cart(theta_1, phi_1)
    # Get directon perpendicular to peak and maximum width direction
    r_2 = np.cross(r_1, r_0)
    r_1_new = np.cross(r_0, r_2)
    assert np.dot(r_1_new, r_1) > 0
    r_1 = r_1_new

    def normalise(v):
        return v / np.linalg.norm(v)
    r_1 = normalise(r_1)
    r_2 = normalise(r_2)

    r = np.dstack(transformations.sph2cart(1, theta, phi))

    # Work out weight for these parameters
    weight = kappa * (np.dot(r, r_0))
    weight += beta * (np.dot(r, r_1)**2 - np.dot(r, r_2)**2)
    return np.exp(weight) * np.cos(theta)


def fisher_dist(theta, phi, kappa, theta_0, phi_0):
    """
    A symmetric distribution on a sphere, centred on a single point.

    Parameters
    ----------
    theta : array_like
        theta values, defined in the range :math:`[-\pi / 2, \pi / 2]`
    phi : array_like
        phi values, defined in the range :math:`[-\pi, \pi]`
    kappa : float
        The 'width' of the distribution. The larger kappa is, the wider the
        distribution
    theta_0 : float
        The theta co-ordinate of the distribution centre
    phi_0 : float
        The phi co-ordinate of the distribution centre

    Returns
    -------
    pdf : array_like
        The probability density at the given (theta, phi) coordinates

    References
    ----------
    'Statistical analysis of spherical data' by Fisher, Lewis, Embleton,
    section 4.4.3

    Examples
    --------
    Fisher distributions with different widths:

    .. literalinclude:: /scripts/fisher_dist.py
    .. image:: /figures/fisher_dist.png
    """
    C = kappa / (4 * np.pi * np.sinh(kappa))
    exp = np.exp(kappa *
                 (np.cos(theta) * np.cos(theta_0) * np.cos(phi - phi_0) +
                  (np.sin(theta) * np.sin(theta_0))))
    return C * exp * np.cos(theta)


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
