"""Helper methods for data import."""
import os

import numpy as np
import astropy.units as u
from collections import OrderedDict

from heliopy import config


def _bytes2str(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in [' B', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.2f %s" % (num, x)
        num /= 1024.0


def cdfpeek(cdf_loc):
    """
    List all the variables present in a CDF file, along with their size.

    Parameters
    ----------
    cdf_loc : string
        Local location of the cdf file.
    """
    import cdflib
    cdf_loc = os.path.expanduser(cdf_loc)
    cdf = cdflib.CDF(cdf_loc)
    info = cdf.cdf_info()
    for key in info:
        print('=' * len(key))
        print(key)
        print('=' * len(key))
        print(info[key])


def listdata(probes=None):
    """
    Print amount of data stored locally in the heliopy data directory.

    Prints a table to the terminal with a column for raw data and a column
    for converted hdf data files.

    Example output ::

        Scanning files in /Users/dstansby/Data/
        ----------------------------------------
        |      Probe |        Raw |        HDF |
        |--------------------------------------|
        |        ace |    1.44 MB |  800.00  B |
        |    cluster |  200.39 MB |    0.00  B |
        |     helios |    2.37 GB |    1.41 GB |
        |        imp |   19.76 MB |   28.56 MB |
        |  messenger |   15.24 MB |   27.21 MB |
        |        mms |   70.11 MB |    0.00  B |
        |     themis |   64.31 MB |    0.00  B |
        |    ulysses |   54.78 MB |   47.98 MB |
        |       wind |  176.84 MB |   63.82 MB |
        |--------------------------------------|
        |--------------------------------------|
        |      Total |    2.96 GB |    1.57 GB |
        ----------------------------------------

    Parameters
    ----------
    probes : List of strings, optional
        Probe names

    """
    data_dir = config['download_dir']
    if probes is None:
        probes = os.listdir(data_dir)

    # Remove directories that start with a .
    probes = [probe for probe in probes if probe[0] != '.']
    probes = sorted(probes)

    sizes = np.zeros((len(probes), 2))
    for i, probe in enumerate(probes):
        probe_dir = os.path.join(data_dir, probe)
        for dirname, dirnames, filenames in os.walk(probe_dir):
            for f in filenames:
                fsize = os.stat(os.path.join(dirname, f)).st_size
                if f.endswith('.hdf'):
                    sizes[i, 1] += fsize
                else:
                    sizes[i, 0] += fsize

    probes.append('Total')
    sizes = np.row_stack((sizes, np.sum(sizes, axis=0)))

    original_sizes = [_bytes2str(size) for size in sizes[:, 0]]
    hdf_sizes = [_bytes2str(size) for size in sizes[:, 1]]

    probes = ['Probe'] + probes
    original_sizes = ['Raw'] + original_sizes
    hdf_sizes = ['HDF'] + hdf_sizes

    def pad(lst):
        maxlen = max([len(item) for item in lst])
        lst = [''.ljust(maxlen - len(item) + 1) + item for item in lst]
        return lst, maxlen

    probes, probelen = pad(probes)
    original_sizes, origlen = pad(original_sizes)
    hdf_sizes, hdflen = pad(hdf_sizes)

    total_len = probelen + origlen + hdflen + 13

    rowfmt = '| {} | {} | {} |'
    divider = '|' + '-' * (total_len - 2) + '|'
    # Do actual printing
    print('Scanning files in {}'.format(data_dir))
    # Header column
    print('-' * total_len)
    # Each probe in turn
    for i, (probe, original_size, hdf_size) in enumerate(
            zip(probes, original_sizes, hdf_sizes)):
        # Add two dividers before total
        if i == len(probes) - 1:
            print(divider)
            print(divider)

        # Print each row
        print(rowfmt.format(probe, original_size, hdf_size))

        # Add one divider after header
        if i == 0:
            print(divider)
    print('-' * total_len)


def cdf_dict(unit_string):
    """
    Method to obtain the unit denoted by the strings inside the CDF files in
    the UNIT attribute.
    """
    ionic_charge = u.def_unit('Charged State', 1.6021766*(10**-19) * u.C)

    units = OrderedDict([('ratio', u.dimensionless_unscaled),
                        ('Unitless', u.dimensionless_unscaled),
                        ('unitless', u.dimensionless_unscaled),
                        ('Spacecraft', u.dimensionless_unscaled),
                        ('microW m^-2', u.mW * u.m**-2),
                        ('years', u.yr),
                        ('days', u.d),
                        ('#/cc', u.cm**-3),
                        ('#/cm^3', u.cm**-3),
                        ('cm^{-3}', u.cm**-3),
                        ('particles cm^-3', u.cm**-3),
                        ('n/cc (from moments)', u.cm**-3),
                        ('n/cc (from fits)', u.cm**-3),
                        ('km/sec (from fits)', u.km / u.s),
                        ('km/sec (from moments)', u.km / u.s),
                        ('ionic charge', u.electron),
                        ('earth radii', u.earthRad),
                        ('Re', u.earthRad),
                        ('Degrees', u.deg),
                        ('degrees', u.deg),
                        ('deg (from fits)', u.deg),
                        ('deg (from moments)', u.deg),
                        ('#/{cc*(cm/s)^3}', (u.cm**3 * (u.cm / u.s)**3)**-1),
                        ('sec', u.s),
                        ('seconds', u.s),
                        ('nT GSE', u.nT),
                        ('nT GSM', u.nT),
                        ('nT DSL', u.nT),
                        ('nT SSL', u.nT),
                        ('msec', u.ms),
                        ('ionic charge', ionic_charge)])
    try:
        return units[unit_string]
    except KeyError:
        return None
