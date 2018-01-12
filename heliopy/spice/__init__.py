"""
SPICE
-----

A module for loading SPICE kernels.

TODO: improve this docstring.
"""
from heliopy import config
import heliopy.data.helper as helper
import heliopy.data.spice as dataspice

import os
from urllib.request import urlretrieve

import numpy as np
import spiceypy as spice
import astropy.units as u

data_dir = config['download_dir']
spice_dir = os.path.join(data_dir, 'spice')

# Required files for all spice calculations
_reqs = ['https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls',
         'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de432s.bsp']


def _setup_spice():
    '''
    Method to download some common files that spice needs to do orbit
    calculations.
    '''
    for kernel in ['lsk', 'planets']:
        loc = dataspice.get_kernel(kernel)
        spice.furnsh(loc)


class SpiceKernel:
    """
    A generic class for a single spice kernel.

    Parameters
    ----------
    spacecraft : str
        Name of the target.
    fname : str, optional
        Filename of a spice kernel to load.

    Attributes
    ----------
    target : str
        The body whose coordinates are being calculated.
    generated : bool
        ``True`` if positions have been generated, ``False`` otherwise.
    times : list
        The list of `datetime` at which positions were last sampled.
    n : int
        The number of samples.
    positions :
        Generated positions.
    observing_body : str
        Observing body
    """
    def __init__(self, target, fname=None):
        local_reqs = _setup_spice()
        spice.furnsh(fname)
        self.target = target
        self.generated = False

    def generate_positions(self, starttime, endtime, n, observing_body, frame):
        """
        Generate positions from a spice kernel.

        Parameters
        ----------
        starttime : datetime
            Start time of positions.
        endtime : datetime
            End time of positions.
        n : int
            Number of positions to generate betweens *starttime* and *endtime*.
        observing_body : str
            The observing body. See https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html
            for a list of allowable bodies.
        frame : str
            The coordinate system to return the positions in.
            See https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/frames.html
            for a list of allowable frames.
        """
        dt = (endtime - starttime)
        # Generate individual times within range
        times = [starttime + (x * dt / n) for x in range(n)]
        # Spice needs a funny set of times
        fmt = '%b %d, %Y'
        etOne = spice.str2et(starttime.strftime(fmt))
        etTwo = spice.str2et(endtime.strftime(fmt))
        spice_times = [x * (etTwo - etOne) / n + etOne for x in range(n)]
        observing_body = observing_body
        # TODO: Work out what "NONE" does here
        positions, lightTimes = spice.spkpos(
            self.target, spice_times, frame, 'NONE', observing_body)
        positions = np.array(positions) * u.km

        self.n = n
        self.times = times
        self.positions = positions
        self.generated = True
