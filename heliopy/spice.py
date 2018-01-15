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

    Objects are initially created using only the body and filename. To perform
    the actual trajectory calculation run `generate_positions`. This generated
    positions are then available via. the attributes :attr:`times` and
    :attr:`positions`.


    Parameters
    ----------
    spacecraft : str
        Name of the target.
    fname : str, optional
        Filename of a spice kernel to load. If ``None``,
        :meth:`heliopy.data.spice.get_kernel` will be used to attempt to find
        or download a kernel corresponding to *spacecraft*.
    """
    def __init__(self, target, fname=None):
        local_reqs = _setup_spice()
        if fname is None:
            fname = dataspice.get_kernel(target)
        spice.furnsh(fname)
        self._target = target
        self._generated = False

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

        self._n = n
        self._times = times
        self._positions = positions
        self._generated = True
        self._observing_body = observing_body

    @property
    def observing_body(self):
        '''
        Observing body
        '''
        return self._observing_body

    @property
    def n(self):
        '''
        The number of samples.
        '''
        return self._n

    @property
    def times(self):
        '''
        The list of `datetime` at which positions were last sampled.
        '''
        return self._times

    @property
    def positions(self):
        '''
        Generated positions.
        '''
        return self._positions

    @property
    def generated(self):
        '''
        ``True`` if positions have been generated, ``False`` otherwise.
        '''
        return self._generated

    @property
    def target(self):
        '''
        The body whose coordinates are being calculated.
        '''
        return self._target
