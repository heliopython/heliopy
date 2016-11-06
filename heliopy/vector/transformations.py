import numpy as np


def cart2sph(x, y, z):
    """
    Given cartesian x, y, z co-ordinates, returns
    shperical r, theta, phi co-ordinates
    """
    xy = x**2 + y**2
    r = np.sqrt(xy + z**2)
    theta = np.arctan2(z, np.sqrt(xy))  # for elevation angle defined from XY-plane up
    phi = np.arctan2(y, x)         # for azimuthal angle defined from x axis counterclockwise
    return r, theta, phi


def sph2cart(r, theta, phi):
    """
    Given spherical r, theta, phi co-orinates, returns cartesian x, y, z
    coordiantes.
    """
    x = r * np.cos(theta) * np.cos(phi)
    y = r * np.cos(theta) * np.sin(phi)
    z = r * np.sin(theta)
    return x, y, z


def angle(v1, v2):
    """
    Return angle between v1 and v2 in radians
    Angle lies between 0 and pi
    """
    assert v1.shape == v2.shape, 'Input vectors must be the same shape'
    v1mag = np.linalg.norm(v1)
    v2mag = np.linalg.norm(v2)
    v1dotv2 = np.dot(v1, v2)

    phi = np.arccos(v1dotv2 / (v1mag * v2mag))
    return phi


def rotationmatrixangle(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    Uses Euler-Rodrigues formula
    """
    assert axis.shape == (3, ), 'Axis must be a single 3 vector'
    assert np.dot(axis, axis) != 0, 'Axis has zero length'

    normaxis = axis / (np.sqrt(np.dot(axis, axis)))

    a = np.cos(theta / 2)
    b, c, d = -normaxis * np.sin(theta / 2)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def rotationmatrix(v):
    """
    Returns the rotation matrix that rotates v onto [0, 0, 1]
    """
    assert v.shape == (3, ), "Input must be a 3 component vector"
    v = np.float64(v)
    zaxis = np.array([0, 0, 1])
    if np.array_equal(v, zaxis):
        return np.ma.identity(3)

    # Calculate orthogonal axis
    orthvec = np.cross(zaxis, v)
    phi = angle(v, zaxis)

    R = rotationmatrixangle(orthvec, -phi)

    newzaxis = np.dot(R, v)
    newzaxis = newzaxis / np.linalg.norm(newzaxis)

    # Check that z axis is [0, 0, 1]
    assert np.abs(newzaxis[0]) < 1e-10, 'Rotation failed, new z axis is: %r' % newzaxis
    assert np.abs(newzaxis[1]) < 1e-10, 'Rotation failed, new z axis is: %r' % newzaxis
    assert newzaxis[2] > 1 - (1e-10), 'Rotation failed, new z axis is: %r' % newzaxis
    assert newzaxis[2] < 1 + (1e-10), 'Rotation failed, new z axis is: %r' % newzaxis

    return R


def changezaxis(x, y, z, newzaxis):
    """
    Rotate 3D cartesian data into a new frame defined by newzaxis
    """
    R = rotationmatrix(newzaxis)
    v = np.row_stack((x, y, z))
    vrot = np.dot(R, v)

    return vrot[0], vrot[1], vrot[2]
