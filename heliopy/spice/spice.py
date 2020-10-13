import pathlib

import numpy as np
import spiceypy
from spiceypy.utils import support_types as spiceytypes
import astropy.time as time
import astropy.units as u
import astropy.coordinates as astrocoords

import sunpy
import sunpy.coordinates as suncoords
import sunpy.sun.constants


# Mapping from SPICE frame name to (frame, frame kwargs)
spice_astropy_frame_mapping = {
    'IAU_SUN': (suncoords.HeliographicCarrington,
                {'observer': suncoords.HeliographicStonyhurst(
                    0 * u.deg, 0 * u.deg, sunpy.sun.constants.radius)}),
}

__all__ = ['furnish', 'Kernel', 'KernelBase', 'SPKKernel',
           'Body', 'Trajectory']


def furnish(kernel):
    """
    Furnish SPICE with a kernel.

    Parameters
    ----------
    fname : `SPKKernel` or list of `SPKKernel`
        SPICE kernel(s) to load.

    See also
    --------
    heliopy.data.spice.get_kernel : For attempting to automatically download
                                    kernels based on spacecraft name.

    """
    if isinstance(kernel, KernelBase):
        kernel = [kernel]
    for k in kernel:
        spiceypy.furnsh(k._fname_str)


class Kernel:
    def __new__(self, fname):
        if pathlib.Path(fname).suffix == '.bsp':
            return SPKKernel(fname)
        else:
            return KernelBase(fname)


class KernelBase:
    """
    Class for a single kernel.

    Notes
    -----
    When creating instances of this class, SPICE is automatically furnished
    with the kernel.
    """
    def __init__(self, fname):
        self._fname = fname
        spiceypy.furnsh(self._fname_str)

    @property
    def fname(self):
        """Path to kernel file."""
        return pathlib.Path(self._fname)

    @property
    def _fname_str(self):
        return str(self.fname)


class SPKKernel(KernelBase):
    """
    A class for a single .spk kernel.

    See also
    --------
    https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/spk.html
    """
    def __init__(self, fname):
        super().__init__(fname)
        # Run bodies() to validate the spice kernel
        self.bodies

    @property
    def bodies(self):
        """List of the bodies stored within the kernel."""
        ids = [int(i) for i in spiceypy.spkobj(self._fname_str)]
        return [Body(i) for i in ids]

    def coverage(self, body):
        """The coverage window for a specified `Body`."""
        coverage = [t for t in spiceypy.spkcov(self._fname_str, body.id)]
        coverage = [spiceypy.et2datetime(t) for t in coverage]
        return coverage


class Body:
    """
    A class for a single body.

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

    def __repr__(self):
        return f'{super().__repr__()}, name={self.name}, id={self.id}'

    def __eq__(self, other):
        return isinstance(other, Body) and other.id == self.id

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
    A class for the trajectory of a single body.

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
    """
    def __init__(self, target):
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
        self._abcorr = str(abcorr)

        # Do the calculation
        pos_vel, lightTimes = spiceypy.spkezr(
            self.target.name, spice_times, frame, self._abcorr,
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
        if self._abcorr.lower() != 'none':
            raise NotImplementedError(
                'Can only convert to astropy coordinates if the aberration '
                'correction is set to "none" '
                f'(currently set to {self._abcorr})')

        frame = spice_astropy_frame_mapping[self._frame][0]

        # Override kwargs for sunpy < 2
        if (frame == suncoords.HeliographicCarrington and
                int(sunpy.__version__[0]) < 2):
            kwargs = {}

        kwargs = spice_astropy_frame_mapping[self._frame][1]
        coords = astrocoords.SkyCoord(
            self.x, self.y, self.z,
            frame=frame, representation_type='cartesian',
            obstime=self.times,
            **kwargs)
        coords.representation_type = frame().default_representation
        return coords

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
    _astropy_frame = spice_astropy_frame_mapping[spice_frame][0]
    Trajectory.coords.__doc__ += \
        f'\n   {spice_frame}, :class:`{_astropy_frame.__name__}`'

Trajectory.coords.__doc__ += '''

If you need the coordinates in another frame, generate them using the 'IAU_SUN'
frame and then use `~astropy.coordinates.SkyCoord.transform_to()` to transform
them into the desired coordinate frame.
'''
