"""Methods for plotting vector fields."""
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import heliopy.time as heliotime


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
