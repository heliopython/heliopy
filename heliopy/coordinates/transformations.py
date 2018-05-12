"""
Coordinate transformation functions

This module contains functions for converting one
:mod:`heliopy.coordinates.frames` object to another.

.. warning::

  The functions in this submodule should never be called directly, transforming
  between coordinate frames should be done using
  :meth:`~astropy.coordinates.BaseCoordinateFrame.transform_to` on coordinate
  frame objects.
"""
import sunpy.coordinates.ephemeris as ephem
import astropy.coordinates as coords
import astropy.units as u
import astropy.coordinates.builtin_frames as astropy_frames
import numpy as np

import heliopy.coordinates.frames as helio_frames


@coords.frame_transform_graph.transform(
    coords.AffineTransform,
    helio_frames.HeliocentricEarthEcliptic,
    helio_frames.GeocentricSolarEcliptic)
def hee_to_gse(hee_coord, gse_frame):
    '''
    Convert from HEE to GSE coordinates.
    '''
    obstime = hee_coord.obstime
    r_earth_sun = ephem.get_sunearth_distance(time=obstime)
    # Rotate 180deg around the z-axis
    R = np.array([[-1, 0, 0],
                  [0, -1, 0],
                  [0, 0, 1]])
    # Offset so centre is at Earth
    offset = coords.CartesianRepresentation(r_earth_sun, 0 * u.m, 0 * u.m)
    return R, offset


# TODO: re-enable this when a custom graph can be built
# __doc__ += astropy_frames._make_transform_graph_docs()
