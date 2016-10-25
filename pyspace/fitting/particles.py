import numpy as np
import scipy.optimize as opt


def maxwellian(x, A, mu, sigma):
    '''
    1-D Maxwellian distribution
    '''
    return A * np.exp(-((v - v0)**2) / (2 * sigma**2))


def bimaxwellian(x, A, mu_1, mu_2, sigma_1, sigma_2):
    '''
    2-D Maxwellian distribution
    '''
    x_1 = x[0]
    x_2 = x[1]
    exponent = (((x_1 - mu_1)**2) / (2 * sigma_1**2)) +\
               (((x_2 - mu_2)**2) / (2 * sigma_2**2))
    return A * np.exp(-exponent)


def bimaxwellianfit(x_1, x_2, f, p0=None):
    '''
    Perform a Bi-Maxwellian fit to data
    '''
    return opt.curve_fit(bimaxwellian, [x_1, x_2], f, p0)
