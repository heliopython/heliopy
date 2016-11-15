"""
Methods for fitting distributions to data
"""
import numpy as np
import scipy.optimize as opt


def maxwellian(x, a, mu, sigma):
    """
    1-D Maxwellian distribution

    Parameters
    ----------
        x : array_like
            x co-ordinates.
        a : float
            Amplitude of distribution.
        mu : float
            Mean of distribution.
        sigma : float
            Standard deviation of distribution

    Returns
    -------
        dist : array_like
            Values of the distribution at corresponding x co-ordinates.
    """
    return a * np.exp(-((x - mu)**2) / (2 * sigma**2))


def bimaxwellian(x, a, mu_1, mu_2, sigma_1, sigma_2):
    """
    2-D Maxwellian distribution

    Parameters
    ----------
        x : list
            x[0] are first co-ordinate values, and x[1] are second co-ordinate
            values
        a : float
            Amplitude of distribution.
        mu_1 : float
            Mean of distribution along first set of co-ordinates.
        mu_2 : float
            Mean of distribution along second set of co-ordinates.
        sigma_1 : float
            Standard deviation of distribution along first set of co-ordinates.
        sigma_2 : float
            Standard deviation of distribution along second set of co-ordinates.

    Returns
    -------
        dist : array_like
            Values of the distribution at corresponding co-ordinates.
    """
    x_1 = x[0]
    x_2 = x[1]
    assert x_1.shape == x_2.shape, 'Coordinate sets must be same shape'
    exponent = (((x_1 - mu_1)**2) / (2 * sigma_1**2)) +\
               (((x_2 - mu_2)**2) / (2 * sigma_2**2))
    return a * np.exp(-exponent)


def poisson(x, rate):
    """
    Poisson distribution

    Parameters
    ----------
        x : array_like
            x values
        rate : float
            Lambda parmeter for Poisson distribution

    Returns
    -------
        dist : array_like
            Values of the distribution at corresponding x co-ordinates.
    """
    return rate * np.exp(-rate * x)


def vonmises(phi, c, alpha, kappa):
    """
    von Mises distribution.

    A symmetric uni-modal distribution used for points
    on the closed interval [0, 2pi].

    Parameters
    ----------
        phi : array_like
            phi co-ordinates.
        c : float
            Amplitude of distribution.
        alpha : float
            Mode of distribution.
        kappa : float
            Kappa parameter. For large kappa this is
            approximately 1/sigma^2, where sigma is
            the tradditional variance of a normal
            distribution.

    Returns
    -------
        dist : array_like
            Values of the distribution at corresponding phi co-ordinates.
    """
    return c * np.exp(kappa * np.cos(phi - alpha))


def maxwellianfit(x, f, p0=None):
    """
    Perform a Maxwellian fit to data

    Parameters
    ----------
        x : array_like
            x values
        f : array_like
            Data points to fit to at corresponding x points
        p0 : list
            Initial guess of fitting parameters. p0[0] is amplitude,
            p0[1] is mean, and p0[2] is standard deviation.

    Returns
    -------
        popt : list
            Optimised parameters. p0[0] is amplitude, p0[1] is mean, and p0[2]
            is standard deviation.
        pcov : list
            Covariance of the estimated parameters. List is in the same order
            as popt.
    """
    return opt.curve_fit(maxwellian, x, f, p0)


def bimaxwellianfit(x_1, x_2, f, p0=None):
    """
    Perform a Bi-Maxwellian fit to data.

    Parameters
    ----------
        x_1 : array_like
            First co-ordinate values.
        x_2 : array_like
            Second co-ordinate values.
        f : array_like
            Data points to fit to at corresponding co-ordinates.
        p0 : list
            Initial guess of fitting parameters. p0[0] is amplitude,
            p0[1] is mean of x_1, p0[2] is mean of x_2, p0[3] is standard
            deviation of x_1, and p0[4] is standard deviation of x_2.

    Returns
    -------
        popt : list
            Optimised parameters. p0[0] is amplitude, p0[1] is mean of x_1,
            p0[2] is mean of x_2, p0[3] is standard deviation of x_1, and p0[4]
            is standard deviation of x_2.
        pcov : list
            Covariance of the estimated parameters. List is in the same order
            as popt.
    """
    return opt.curve_fit(bimaxwellian, [x_1, x_2], f, p0)


def poissonfit(x, f, p0=None):
    """
    Perform a Poisson distribution fit to data

    Parameters
    ----------
        x : array_like
            x values
        f : array_like
            Data points to fit to at corresponding x points
        p0 : list
            Initial guess of fitting parameters. p0[0] is rate.

    Returns
    -------
        popt : list
            Optimised parameters. p0[0] is rate.
        pcov : list
            Covariance of the estimated parameters. List is in the same order
            as popt.
    """
    return opt.curve_fit(poisson, x, f, p0)


def vonmisesfit(phi, f, p0=None):
    """Perform a Von mises fit to data

    Parameters
    ----------
        phi : array_like
            phi co-ordinates.
        f : array_like
            Data points to fit to at corresponding phi points.
        p0 : list
            Initial guess of fitting parameters. p0[0] is alpha factor, p0[1] is
            kappa factor.

    Returns
    -------
        popt : list
            Optimised parameters.p0[0] is alpha factor, p0[1] is kappa factor.
        pcov : list
            Covariance of the estimated parameters. List is in the same order
            as popt.
    """
    return opt.curve_fit(vonmises, phi, f, p0)
