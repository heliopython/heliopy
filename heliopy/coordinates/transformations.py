"""
Coordinate transformation functions

This module contains functions for converting one `sunpy.coordinates.frames`
object to another.

.. warning::

  The functions in this submodule should never be called directly, transforming
  between coordinate frames should be done using
  `~astropy.coordinates.BaseCoordinateFrame.transform_to` methods
  of `~astropy.coordinates.BaseCoordinateFrame`.
"""
from astropy.coordinates.baseframe import frame_transform_graph
from astropy.coordinates.builtin_frames import _make_transform_graph_docs
from astropy.coordinates.transformations import FunctionTransform
from astropy.coordinates.builtin_frames import HeliocentricTrueEcliptic
from astropy.coordinates.builtin_frames.utils import EQUINOX_J2000
from astropy.coordinates.matrix_utilities import (rotation_matrix,
                                                  matrix_product)


from heliopy.coordinates.frames import (HeliocentricEarthEcliptic)
__all__ = ['hee_to_hte']


def _euler_rotation_matrix(omega, theta, phi):
    '''
    Return the euler rotaiton matrix given by the arguments. Rotations are
    done in the 'zxz' order.
    '''
    r1 = rotation_matrix(omega, axis='z')
    r2 = rotation_matrix(theta, axis='x')
    r3 = rotation_matrix(phi, axis='z')
    return matrix_product(*matrices[::-1])


@baseframe.frame_transform_graph.transform(FunctionTransform,
                                           HeliocentricEarthEcliptic,
                                           HeliocentricTrueEcliptic)
def hee_to_hte(heecoord, htecoord):
    """
    Transform from HeliocentricEarthEcliptic to HeliocentricTrueEcliptic.

    The resulting HTE frame has the same equinox as the input HEE frame.
    """
    omega = 0
    theta = 0
    lambda_mean = 100.4664568 + 35999.3728565 * (heecoord.equinox - EQUINOX_J2000)
    g = lambda_mean -
    phi = labmda_mean + 1.915 * np.sin()
    rot_matrix = _euler_rotation_matrix(omega, theta, lambda_mean)
