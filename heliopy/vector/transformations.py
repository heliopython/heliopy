import numpy as np


def pol2cart(r, phi):
    """
    Given polar r, phi co-ordinates, returns cartesian x, y co-ordinates.

    Parameters
    ----------
        r : array_like
            r values
        phi : array_like
            Azimuthal angle values.

    Returns
    -------
        x : array_like
            x values
        y : array_like
            y values

    """
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return x, y


def cart2pol(x, y):
    """
    Given cartesian x, y co-ordinates, returns polar r, phi co-ordinates.

    Parameters
    ----------
        x : array_like
            x values
        y : array_like
            y values

    Returns
    -------
        r : array_like
            r values
        phi : array_like
            Azimuthal angle values.
    """
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return r, phi


def cart2sph(x, y, z):
    """
    Given cartesian x, y, z co-ordinates, returns shperical r, theta, phi
    co-ordinates.

    Parameters
    ----------
        x : array_like
            x values
        y : array_like
            y values
        z : array_like
            z values

    Returns
    -------
        r : array_like
            r values
        theta : array_like
            Elevation angles defined from the x-y plane towards the z-axis
        phi : array_like
            Azimuthal angles defined in the x-y plane, clockwise about the
            z-axis, from the x-axis.
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

    Parameters
    ----------
        r : array_like
            r values
        theta : array_like
            Elevation angles defined from the x-y plane towards the z-axis
        phi : array_like
            Azimuthal angles defined in the x-y plane, clockwise about the
            z-axis, from the x-axis.

    Returns
    -------
        x : array_like
            x values
        y : array_like
            y values
        z : array_like
            z values

    """
    x = r * np.cos(theta) * np.cos(phi)
    y = r * np.cos(theta) * np.sin(phi)
    z = r * np.sin(theta)
    return x, y, z


def angle(v1, v2):
    """
    Return angle between vectors v1 and v2 in radians.

    Parameters
    ----------
        v1 : array_like
            Vector 1.
        v2: array_like
            Vector 2.

    Returns
    -------
        phi : float
            Angle between two vectors in radians.
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
    the given axis by theta. Uses Euler-Rodrigues formula.

    Parameters
    ----------
        axis : array_like
            Axis to rotate about.
        theta : float
            Angle through which to rotate in radians.

    Returns
    -------
        R : array_like
            Rotation matrix resulting from rotation about given axis.
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
    Returns the rotation matrix that maps the input vector on to the z-axis.

    Parameters
    ----------
        v : array_like
            Input vector.

    Returns
    -------
        R : array_like
            Rotation matrix.
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
    Rotate 3D cartesian data into a new frame where newzaxis is the z-axis.

    Parameters
    ----------
        x : array_like
            x values.
        y : array_like
            y values.
        z : array_like
            z values.

    Returns
    -------
        newx : array_like
            Rotated x values.
        newy : array_like
            Rotated y values.
        newz : array_like
            Rotated values.
    """
    R = rotationmatrix(newzaxis)
    v = np.row_stack((x, y, z))
    vrot = np.dot(R, v)

    return vrot[0], vrot[1], vrot[2]
