"""m
Creating coordinate objects
---------------------------
Coordinate objects can be created using the coordinate frame classes in
:mod:`heliopy.coordinates.frames`, for example, to create a coordinate in
a GSE frame:

    >>> from datetime import datetime
    >>> from astropy.constants import au
    >>> import heliopy.coordinates.frames as frames
    >>> gse_coord = frames.GeocentricSolarEcliptic(1 * au, 0 * au, 0 * au)
    >>> gse_coord
    <GeocentricSolarEcliptic Coordinate (obstime=None): (x, y, z) in m
        (1.49597871e+11, 0., 0.)>

Transforming between coordinate systems
---------------------------------------
TODO: Add examples here
"""
