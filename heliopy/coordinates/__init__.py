"""
Creating coordinate objects
---------------------------
Coordinate objects can be created using the coordinate frame classes in
:mod:`heliopy.coordinates.frames`, for example, to create a coordinate in
a GSE frame:

    >>> from astropy.constants import au
    >>> import heliopy.coordinates.frames as frames
    >>> hee_coord = frames.HeliocentricEarthEcliptic(1 * au, 0 * au, 0 * au)
    >>> hee_coord
    <HeliocentricEarthEcliptic Coordinate (obstime=None): (x, y, z) in m
        (1.49597871e+11, 0., 0.)>

Transforming between coordinate systems
---------------------------------------
To transform between coordinate frames, the ``transform_to()`` method can be
called on a coordinate object:

    >>> from datetime import datetime
    >>> from astropy.constants import au
    >>> import heliopy.coordinates.frames as frames
    >>>
    >>> hee_coord = frames.HeliocentricEarthEcliptic(1 * au, 0 * au, 0 * au,
    ...     obstime=datetime(1992, 12, 21))
    >>> gse_coord = hee_coord.transform_to(frames.GeocentricSolarEcliptic)
    >>> gse_coord
    <GeocentricSolarEcliptic Coordinate (obstime=None): (x, y, z) in m
        (-2.42947355e+09, 0., 0.)>
"""
