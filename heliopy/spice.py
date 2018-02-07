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
    fname : str or list
        Filename of a spice kernel to load, or list of filenames to load.

    See also
    --------
    heliopy.data.spice.get_kernel : For attempting to automatically download
                                    kernels based on spacecraft name.

    """
    if isinstance(fname, str):
        fname = [fname]
    for f in fname:
        spiceypy.furnsh(f)


class Trajectory:
    """
    A generic class for the trajectory of a single body.

    Objects are initially created using only the body. To perform
    the actual trajectory calculation run :meth:`generate_positions`.
    The generated positions are then available via. the attributes
    :attr:`times`, :attr:`x`, :attr:`y`, and :attr:`z`.

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

    def generate_positions(self, times, observing_body, frame):
        """
        Generate positions from a spice kernel.

        Parameters
        ----------
        times : iterable of `datetime`
            An iterable (e.g. a `list`) of `datetime` objects at which the
            positions are calculated.
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
        # Spice needs a funny set of times
        fmt = '%b %d, %Y'
        spice_times = [spiceypy.str2et(time.strftime(fmt)) for time in times]
        observing_body = observing_body
        # 'None' specifies no light-travel time correction
        positions, lightTimes = spiceypy.spkpos(
            self.target, spice_times, frame, 'None', observing_body)
        positions = np.array(positions) * u.km

        self._times = times
        self._positions = positions
        self._x = positions[:, 0]
        self._y = positions[:, 1]
        self._z = positions[:, 2]
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
    def times(self):
        '''
        The `list` of `datetime` at which positions were last sampled.
        '''
        return self._times

    @property
    def x(self):
        '''
        x coordinates of position.
        '''
        return self._x

    @property
    def y(self):
        '''
        y coordinates of position.
        '''
        return self._y

    @property
    def z(self):
        '''
        z coordinates of position.
        '''
        return self._z

    @property
    def r(self):
        '''
        Magnitude of position vectors.
        '''
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

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

    def change_units(self, unit):
        """
        Convert the positions to different units.

        Parameters
        ----------
        unit : astropy.units.Quantity
            Must be a unit of length (e.g. km, m, AU).
        """
        self._x = self._x.to(unit)
        self._y = self._y.to(unit)
        self._z = self._z.to(unit)
        self._positions = self._positions.to(unit)
