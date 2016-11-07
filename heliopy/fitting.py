"""
Methods for fitting distributions to data
"""
import numpy as np
import scipy.optimize as opt
import scipy.special as special


def maxwellian(x, a, mu, sigma):
    """
    1-D Maxwellian distribution

    Parameters
    ----------
        x : array_like
            x values
        a : float
            Amplitude
        mu : float
            Mean of distribution
        sigma : float
            Standard deviation of distribution
    """
    return a * np.exp(-((x - mu)**2) / (2 * sigma**2))


def bimaxwellian(x, a, mu_1, mu_2, sigma_1, sigma_2):
    """
    2-D Maxwellian distribution
    """
    x_1 = x[0]
    x_2 = x[1]
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
            phi values
        c : float
            Amplitude of distribution
        alpha : float
            Mode of distribution
        kappa : float
            Kappa parameter. For large kappa this is
            approximately 1/sigma^2, where sigma is
            the tradditional variance of a normal
            distribution.

    Returns
    -------
        pdf : array_like
            Probability desnity function at corresponding
            phi values.
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
    """
    return opt.curve_fit(maxwellian, x, f, p0)


def bimaxwellianfit(x_1, x_2, f, p0=None):
    """Perform a Bi-Maxwellian fit to data"""
    return opt.curve_fit(bimaxwellian, [x_1, x_2], f, p0)


def poissonfit(x, f, p0=None):
    """Perform a Poisson distribution fit to data"""
    return opt.curve_fit(poisson, x, f, p0)


def vonmisesfit(phi, f, p0=None):
    """Perform a Von mises fit to data"""
    return opt.curve_fit(vonmises, phi, f, p0)
