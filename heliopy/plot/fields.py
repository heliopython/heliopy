"""Methods for plotting vector fields."""
import matplotlib.pyplot as plt
import numpy as np

import heliopy.time as heliotime
import heliopy.vector.transformations as trans


def thetaphi(x, y, z):
    """
    Plots a 'theta-phi map' given 3D cartesian data.

    Parameters
    ----------
        x: array_like
            x data values
        y: array_like
            y data values
        z: array_like
            z data values
    """
    _, theta, phi = trans.cart2sph(x, y, z)

    ax = plt.gca()
    ax.hexbin(phi, theta,
              C=1 / np.cos(theta),
              reduce_C_function=np.sum,
              bins='log',
              mincnt=1,
              cmap='gray_r')

    # Add guide lines
    ax.axhline(0, color='k', alpha=0.5)
    ax.axvline(0, color='k', alpha=0.5)
    ax.axvline(-np.deg2rad(90), color='k', alpha=0.5)
    ax.axvline(np.deg2rad(90), color='k', alpha=0.5)
    # Axis labels
    ax.set_xlabel(r'$\phi$')
    ax.set_ylabel(r'$\theta$')


def advectedfield(t, x, y, z, vx, vy, vz, **kwargs):
    """
    Plots time series measurements of a vector field spatially.

    `x`, `y`, `z` are the vector field components, and `vx`, `vy`, `vz` are the
    advected velocities of the field. The conversion from time to spatial
    co-ordinates is done using r = t * v.

    kwargs are passed to `plt.quiver()`.

    Parameters
    ----------
        t : array_like
            Times at which vectors were measured. Data either be `float`, which
            is interpreted as seconds, or `dtime`.
        x : array_like
            x values of vector field.
        y : array_like
            y values of vector field.
        z : array_like
            z values of vector field.
        vx : float
            Advected velocity in the x direction
        vy : float
            Advected velocity in the y direction
        vz : float
            Advected velocity in the z direction
    """
    # Convert from datetime to seconds since initial time
    t = np.array(t)
    if np.issubdtype(t.dtype, np.datetime64):
        t = heliotime.nptimedelta2seconds(t - t[0])

    rx = vx * t
    ry = vy * t
    rz = vz * t

    ax = plt.gca()
    ax.quiver(rx, ry, rz, x, y, z, pivot='tail', **kwargs)
