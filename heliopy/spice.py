from heliopy import config
import heliopy.data.helper as helper
import heliopy.data.spice as dataspice

import os

import numpy as np
import spiceypy
import astropy.units as u

data_dir = config['download_dir']
spice_dir = os.path.join(data_dir, 'spice')


def _setup_spice():
    '''
    Method to download some common files that spice needs to do orbit
    calculations.
    '''
    for kernel in ['lsk', 'planets']:
        loc = dataspice.get_kernel(kernel)
        spiceypy.furnsh(loc)


def furnish(fname):
    """
    Furnish SPICE with a kernel.

    Parameters
    ----------
    fname : Filename of a spice kernel to load.

    See also
    --------
    heliopy.data.spice.get_kernel : For attempting to automatically download
                                    kernels based on spacecraft name.

    """
    spiceypy.furnsh(fname)


class Trajectory:
    """
    A generic class for the trajectory of a single body.

    Objects are initially created using only the body. To perform
    the actual trajectory calculation run `generate_positions`. This generated
    positions are then available via. the attributes :attr:`times` and
    :attr:`positions`.

    Parameters
    ----------
    spacecraft : str
        Name of the target. The name must be present in the loaded kernels.

    Notes
    -----
    When an instance of this class is created, a leapseconds kernel and a
    planets kernel are both automatically loaded.

    See also
    --------
    furnish : for loading in local spice kernels.
    """
    def __init__(self, target):
        _setup_spice()
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
            The observing body. Output position vectors are given relative to
            the position of this body.
            See https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html
            for a list of bodies.
        frame : str
            The coordinate system to return the positions in.
            See https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/frames.html
            for a list of frames.
        """
        dt = (endtime - starttime)
        # Generate individual times within range
        times = [starttime + (x * dt / n) for x in range(n)]
        # Spice needs a funny set of times
        fmt = '%b %d, %Y'
        etOne = spiceypy.str2et(starttime.strftime(fmt))
        etTwo = spiceypy.str2et(endtime.strftime(fmt))
        spice_times = [x * (etTwo - etOne) / n + etOne for x in range(n)]
        observing_body = observing_body
        # 'None' specifies no light-travel time correction
        positions, lightTimes = spiceypy.spkpos(
            self.target, spice_times, frame, 'None', observing_body)
        positions = np.array(positions) * u.km

        self._times = times
        self._positions = positions
        self._generated = True
        self._observing_body = observing_body

    @property
    def observing_body(self):
        '''
        Observing body. The position vectors are all specified relative to
        this body.
        '''
        return self._observing_body

    @property
    def n(self):
        '''
        The number of position samples.
        '''
        return len(times)

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
