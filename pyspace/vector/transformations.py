import numpy as np


def cart2sph(x, y, z):
    '''
    Given cartesian x, y, z co-ordinates, returns
    shperical r, theta, phi co-ordinates
    '''
    xy = x**2 + y**2
    r = np.sqrt(xy + z**2)
    theta = np.arctan2(z, np.sqrt(xy))  # for elevation angle defined from XY-plane up
    phi = np.arctan2(y, x)         # for azimuthal angle defined from x axis counterclockwise
    return r, theta, phi
