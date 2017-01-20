"""Methods for plotting vector fields."""
import matplotlib.pyplot as plt
import numpy as np

import heliopy.time as heliotime
import heliopy.vector.transformations as trans


def jointdists(data, title=None, **kwargs):
    """
    Plots joint distributions for 3D field data on a single figure.

    Uses the current figure if created, or if no figures are created a new one
    is created. `**kwargs` are passed to plt.hexbin, which does the
    distribution plotting.

    Parameters
    ----------
        data : DataFrame
            The data must be a pandas DataFrame, with each independent variable
            in the columns.
        title : string, optional
            If specified, the given `title` is added to the top of the figure.
    """
    # Set the same axis limits for each plot
    plotlim = data.abs().max().max()
    extent = (-plotlim, plotlim, -plotlim, plotlim)
    labels = list(data)
    n = len(labels) - 1
    fig = plt.gcf()
    axs = fig.subplots(n, n,
                       gridspec_kw={'hspace': 0, 'wspace': 0})
    for i in range(0, n):
        for j in range(0, n):
            if i < j:
                axs[i, j].axis('off')
            else:
                axs[i, j].set_xlim(left=-plotlim, right=plotlim)
                axs[i, j].set_aspect('equal')
                im = axs[i, j].hexbin(data[labels[j]], data[labels[i + 1]],
                                      extent=extent, mincnt=1,
                                      cmap='gray_r',
                                      bins='log')
                if i == n - 1:
                    axs[i, j].set_xlabel(labels[j])
                if j == 0:
                    axs[i, j].set_ylabel(labels[i + 1])
    if title is not None:
        fig.suptitle(title)


def thetaphi(x, y, z):
    """
    Plots a 'theta-phi map' given 3D cartesian data.

    Theta values are defined between [-pi / 2, pi / 2], with theta=0 being the
    x-y plane.

    Phi values are defined between [-pi, pi], with phi = 0 along the x-axis.

    Parameters
    ----------
        x: array_like
            x data values
        y: array_like
            y data values
        z: array_like
            z data values

    Examples
    --------
    A theta-phi plot for a single day of WIND magnetic field data:

    .. literalinclude:: /scripts/plot_thetaphi.py
    .. image:: /figures/plot_thetaphi.png
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
    # Axis limits
    ax.set_xlim(left=-np.pi, right=np.pi)
    ax.set_ylim(bottom=-np.pi / 2, top=np.pi / 2)


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
