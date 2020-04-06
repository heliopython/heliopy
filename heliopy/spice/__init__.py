"""
Overview
--------
`SPICE`_ is a NASA toolkit for calculating the position of bodies
(including planets and spacecraft) within the solar system. This module builds
on the `spiceypy`_ package to provide a high level interface to the SPICE
toolkit for performing orbital calculations using spice kernels.

Integration with :mod:`astropy.coordinates`
-------------------------------------------
As well as allowing positions to be calculated in any coordinate system defined
in the `SPICE`_ toolkit, :mod:`heliopy.spice` can also construct
:class:`astropy.coordinates.SkyCoord` objects if the frame is implemented in
astropy or SunPy. See the documentaiton of
:meth:`heliopy.spice.Trajectory.coords()` for information on which frames are
supported.

.. _SPICE: https://naif.jpl.nasa.gov/naif/toolkit.html
.. _spiceypy: https://spiceypy.readthedocs.io/en/master/
"""

from heliopy import config
import heliopy.data.helper as helper
import heliopy.data.spice as dataspice

import os

import numpy as np
import spiceypy
from spiceypy.utils import support_types as spiceytypes
import astropy.time as time
import astropy.units as u
import astropy.coordinates as astrocoords
import sunpy.coordinates as suncoords

_SPICE_SETUP = False


def _setup_spice():
    '''
    Method to download some common files that spice needs to do orbit
    calculations.
    '''
    global _SPICE_SETUP
    if not _SPICE_SETUP:
        for kernel in dataspice.generic_kernels:
            loc = dataspice.get_kernel(kernel.short_name)
            spiceypy.furnsh(loc)
        _SPICE_SETUP = True


spice_astropy_frame_mapping = {
    'J2000': astrocoords.ICRS,
    'IAU_SUN': suncoords.HeliographicCarrington,
}


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


class Body:
    """
    A generic class for a single body.

    Parameters
    ----------
    body : `int` or `str`
        Either the body ID code or the body name.
    """
    def __init__(self, body):
        if isinstance(body, int):
            self.id = body
        elif isinstance(body, str):
            self.name = body
        else:
            raise ValueError('body must be an int or str')

    @property
    def id(self):
        """Body id code."""
        return self._id

    @id.setter
    def id(self, id):
        self._id = id
        try:
            self._name = spiceypy.bodc2n(id)
        except spiceytypes.SpiceyError:
            raise ValueError(f'id "{id}" not known by SPICE')

    @property
    def name(self):
        """Body name."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        try:
            self._id = spiceypy.bodn2c(name)
        except spiceytypes.SpiceyError:
            raise ValueError(f'Body name "{name}" not known by SPICE')


class Trajectory:
    """
    A generic class for the trajectory of a single body.

    Objects are initially created using only the body. To perform
    the actual trajectory calculation run :meth:`generate_positions`.
    The generated positions are then available via. the attributes
    :attr:`times`, :attr:`x`, :attr:`y`, and :attr:`z`.

    Parameters
    ----------
    target : str
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
        self._target = Body(target)
        self._generated = False

    def generate_positions(self, times, observing_body, frame,
                           abcorr=None):
        """
        Generate positions from a spice kernel.

        Parameters
        ----------
        times : time like
            An object that can be parsed by `~astropy.time.Time`.
        observing_body : str or int
            The observing body. Output position vectors are given relative to
            the position of this body. See
            https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html
            for a list of bodies.
        frame : str
            The coordinate system to return the positions in. See
            https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/frames.html
            for a list of frames.
        abcorr : str, optional
            By default no aberration correciton is performed.
            See the documentaiton at
            https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkezr_c.html
            for allowable values and their effects.
        """
        times = time.Time(times)
        # Spice needs a funny set of times
        fmt = '%Y %b %d, %H:%M:%S'
        spice_times = [spiceypy.str2et(time.strftime(fmt)) for time in times]
        abcorr = str(abcorr)

        # Do the calculation
        pos_vel, lightTimes = spiceypy.spkezr(
            self.target.name, spice_times, frame, abcorr,
            observing_body)

        positions = np.array(pos_vel)[:, :3] * u.km
        velocities = np.array(pos_vel)[:, 3:] * u.km / u.s

        self._frame = frame
        self._times = time.Time(times)
        self._velocities = velocities
        self._x = positions[:, 0]
        self._y = positions[:, 1]
        self._z = positions[:, 2]
        self._vx = velocities[:, 0]
        self._vy = velocities[:, 1]
        self._vz = velocities[:, 2]
        self._generated = True
        self._observing_body = Body(observing_body)

    @property
    def observing_body(self):
        '''
        Observing `Body`. The position vectors are all specified relative to
        this body.
        '''
        return self._observing_body

    @property
    def spice_frame(self):
        """
        The coordinate frame used by SPICE.
        """
        return self._spice_frame

    @property
    def times(self):
        '''
        A :class:`~astropy.time.Time` object containing the times sampled.
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
    def coords(self):
        """
        A :class:`~astropy.coordinates.SkyCoord` object.
        """
        if self._frame not in spice_astropy_frame_mapping:
            raise ValueError(f'Current frame "{self._frame}" not in list of '
                             f'known coordinate frames implemented in astropy '
                             f'or sunpy ({spice_astropy_frame_mapping})')

        frame = spice_astropy_frame_mapping[self._frame]
        return astrocoords.SkyCoord(
            self.x, self.y, self.z,
            frame=frame, representation_type='cartesian',
            obstime=self.times)

    @property
    def vx(self):
        """
        x component of velocity.
        """
        return self._vx

    @property
    def vy(self):
        """
        y component of velocity.
        """
        return self._vy

    @property
    def vz(self):
        """
        z component of velocity.
        """
        return self._vz

    @property
    def velocity(self):
        """
        Velocity.

        Returned as a shape ``(n, 3)`` array, where the ``n`` axis
        is the time axis.
        """
        return self._velocities

    @property
    def speed(self):
        '''
        Speed (magnitude of velocity vectors).
        '''
        return np.sqrt(self.vx**2 + self.vy**2 + self.vz**2)

    @property
    def generated(self):
        '''
        ``True`` if positions have been generated, ``False`` otherwise.
        '''
        return self._generated

    @property
    def target(self):
        '''
        The `Body` whose coordinates are being calculated.
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


Trajectory.coords.__doc__ += '''

Notes
-----
The following frames are supported:

.. csv-table::
   :name: supported_python_coords
   :header: "Spice name", "SkyCoord class"
   :widths: 20, 20
'''

for spice_frame in spice_astropy_frame_mapping:
    _astropy_frame = spice_astropy_frame_mapping[spice_frame]
    Trajectory.coords.__doc__ += \
        f'\n   {spice_frame}, :class:`{_astropy_frame.__name__}`'
