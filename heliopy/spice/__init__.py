"""
A module for loading spice kernels.

TODO: improve this docstring.
"""
from heliopy import config
import heliopy.data.helper as helper

import os
from urllib.request import urlretrieve

import numpy as np
import spiceypy as spice

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
    general_dir = os.path.join(spice_dir, 'generic')
    if not os.path.exists(general_dir):
        print('Creating {} directory'.format(general_dir))
        os.makedirs(general_dir)

    local_reqs = []
    for req in _reqs:
        fname = req.split('/')[-1]
        local_loc = os.path.join(general_dir, fname)
        if not os.path.exists(local_loc):
            print('Downloading {}'.format(req))
            urlretrieve(req, local_loc, reporthook=helper._reporthook)
            local_reqs.append(local_loc)
    return local_reqs


class SpiceKernel:
    """
    A generic class for a single spice kernel.

    Parameters
    ----------
    fname : str, optional
        Filename of a spice kernel to load.
    spacecraft : str, optional
        Name of the spacecraft to automatically load. For a list of
        supported spacecraft TODO!

    Attributes
    ----------
    generated : bool
    times : list
    n : int
    positions :
    """
    def __init__(self, target, fname=None):
        if fname is None and spacecraft is None:
            raise ValueError('Either a filename or a spacecraft must be '
                             'provided.')
        local_reqs = _setup_spice()
        for req in local_reqs:
            spice.furnsh(req)
        spice.furnsh(fname)
        self.target = target
        self.generated = False

    def generate_positions(self, starttime, endtime, n, observing_body):
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
        """
        # TODO: Make this accept the input times
        utc = ['Mar 1, 2020', 'Dec 31, 2028']
        etOne = spice.str2et(utc[0])
        etTwo = spice.str2et(utc[1])
        # Generate individual times within range
        spice_times = [x * (etTwo - etOne) / n + etOne for x in range(n)]
        observing_body = observing_body
        # TODO: Make this an argument
        frame = 'ECLIPJ2000'
        # TODO: Work out what "NONE" does here
        positions, lightTimes = spice.spkpos(
            self.target, spice_times, 'ECLIPJ2000', 'NONE', observing_body)
        positions = np.array(positions)
        # TODO: Work out how to return these using units or coordinates
        # Positions is a nx3 vector of XYZ positions
        # Convert from km to AU
        positions = positions / 1.496e8

        self.n = n
        # TODO: Make this a list of datetimes or similar
        self.times = spice_times
        self.positions = positions
        self.generated = True
