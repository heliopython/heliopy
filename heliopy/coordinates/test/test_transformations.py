import heliopy.coordinates.frames as frames
import astropy.units as u
from datetime import datetime


def test_hee_to_gse():
    t = datetime(1992, 12, 21)
    hee = frames.HeliocentricEarthEcliptic(
        x=0.1*u.au, y=1*u.km, z=1*u.km, obstime=t)
    gse = hee.transform_to(frames.GeocentricSolarEcliptic)
    assert gse.z == hee.z
    assert gse.y == -hee.y
    assert gse.x > 0 * u.km
    assert gse.x > hee.x
