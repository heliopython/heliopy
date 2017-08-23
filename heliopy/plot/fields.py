"""Methods for plotting vector fields."""
import matplotlib.pyplot as plt
import numpy as np

import heliopy.time as heliotime


def jointdists(data, title=None, sharelims=True, **kwargs):
    """
    Plots joint distributions for 3D field data on a single figure.

    Uses the current figure if created, or if no figures are created a new one
    is created. `**kwargs` are passed to
    :py:func:`matplotlib:matplotlib.pyplot.hexbin`, which does the distribution
    plotting.

    Parameters
    ----------
    data : DataFrame
        The data must be a pandas DataFrame, with each independent variable
        in the columns.
    title : string, optional
        If specified, the given `title` is added to the top of the figure
    sharelims : bool, optional
        If *True*, all joint distributions will share the same axis limits,
        which will be set by the minimum and maximum values of the combined
        dataset.

        If *False*, each distribution will automatically scale it's own axis.

        Default is *True*

    Examples
    --------
    A joint distribution plot for a single day of WIND magnetic field data:

    .. literalinclude:: /scripts/plot_jointdists.py
    .. image:: /figures/plot_jointdists.png
    """
    if sharelims:
        # Set the same axis limits for each plot
        plotlim = data.abs().max().max()
        extent = (-plotlim, plotlim, -plotlim, plotlim)
    else:
        extent = None

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
                if sharelims:
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
    return axs


def thetaphi(x, y, z):
    r"""
    Plots a 'theta-phi map' given 3D cartesian data.

    Theta values are defined between
    :math:`[-\pi /2, \pi / 2]`, with :math:`\theta = 0` being the x-y plane.

    Phi values are defined between :math:`[-\pi, \pi]`, with :math:`\phi = 0`
    along the x-axis.

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
    phi = np.atan2(y, x)
    theta = np.atan2(z, np.sqrt(x**2 + y**2))

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
    return ax
