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
    probes : list
        Probe names as a list of strings.
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
    ionic_charge = u.def_unit('Charged State', 1.6021766 * (10**-19) * u.C)

    units = OrderedDict([('ratio', u.dimensionless_unscaled),
                        ('Na', u.dimensionless_unscaled),
                        ('NOTEXIST', u.dimensionless_unscaled),
                        ('Unitless', u.dimensionless_unscaled),
                        ('unitless', u.dimensionless_unscaled),
                        ('Spacecraft', u.dimensionless_unscaled),
                        ('Quality_Flag', u.dimensionless_unscaled),
                        ('(0=No Gap)', u.dimensionless_unscaled),
                        ('(1=good)', u.dimensionless_unscaled),
                        ('(Instrmt Coords)', u.dimensionless_unscaled),
                        ('(222/223=good)', u.dimensionless_unscaled),
                        ('32-bit error flags', u.dimensionless_unscaled),
                        ('del-phi counts', u.dimensionless_unscaled),
                        ('(10=He_OK,>1=P_OK)', u.dimensionless_unscaled),
                        ('(1=NTMS,2=TMS,3=AQM)', u.dimensionless_unscaled),
                        ('(1=SW,2=MULT,3=NSW)', u.dimensionless_unscaled),
                        ('None', u.dimensionless_unscaled),
                        ('none', u.dimensionless_unscaled),
                        ('8=IMP8', u.dimensionless_unscaled),
                        (' index value', u.dimensionless_unscaled),
                        (' none', u.dimensionless_unscaled),
                        ('Samples/cycle', u.dimensionless_unscaled),
                        (('[fraction]'), u.dimensionless_unscaled),
                        ('DD-MMM-YYYY_hr:mm', u.dimensionless_unscaled),
                        ('(6=No,1=All,-1=n/a)', u.dimensionless_unscaled),
                        ('Ticks', u.dimensionless_unscaled),
                        ('cnts',  u.dimensionless_unscaled),
                        ('#',  u.dimensionless_unscaled),

                        ('microW m^-2', u.mW * u.m**-2),

                        ('years', u.yr),
                        ('(2038=Yr0)', u.yr),
                        ('days', u.d),

                        ('#/cc', u.cm**-3),
                        ('#/cm^3', u.cm**-3),
                        ('cm^{-3}', u.cm**-3),
                        ('particles cm^-3', u.cm**-3),
                        ('n/cc (from moments)', u.cm**-3),
                        ('n/cc (from fits)', u.cm**-3),
                        ('Per cc', u.cm**-3),
                        ('#/cm3', u.cm**-3),
                        ('n/cc', u.cm**-3),

                        ('km/sec', u.km / u.s),
                        ('km/sec (from fits)', u.km / u.s),
                        ('km/sec (from moments)', u.km / u.s),
                        ('Km/s', u.km / u.s),

                        ('km (>200)', u.km),
                        ('ionic charge', u.dimensionless_unscaled),
                        ('u/e', u.dimensionless_unscaled),
                        ('Volts', u.V),

                        ('earth radii', u.earthRad),
                        ('Re', u.earthRad),
                        ('Earth Radii', u.earthRad),
                        ('Re (1min)', u.earthRad),
                        ('Re (1hr)', u.earthRad),

                        ('Degrees', u.deg),
                        ('degrees', u.deg),
                        ('Deg', u.deg),
                        ('deg (from fits)', u.deg),
                        ('deg (from moments)', u.deg),
                        ('deg (>200)', u.deg),

                        ('Deg K', u.K),
                        ('deg_K', u.K),
                        ('#/{cc*(cm/s)^3}', (u.cm**3 * (u.cm / u.s)**3)**-1),
                        ('sec', u.s),
                        ('Samples/s', 1 / u.s),

                        ('seconds', u.s),
                        ('nT GSE', u.nT),
                        ('nT GSM', u.nT),
                        ('nT DSL', u.nT),
                        ('nT SSL', u.nT),
                        ('nT (1min)', u.nT),
                        ('nT (3sec)', u.nT),
                        ('nT (1hr)', u.nT),
                        ('nT (>200)', u.nT),

                        ('msec', u.ms),
                        ('milliseconds', u.ms),

                        ('MeV/nuc', u.MeV),

                        ('ionic charge', ionic_charge),
                        ('#/cm2-ster-eV-sec',
                         1 / (u.cm**2 * u.sr * u.eV * u.s)),
                        ('#/(cm^2*s*sr*Mev/nucleon)',
                         1 / (u.cm**2 * u.sr * u.MeV * u.s)),
                        ('#/(cm^2*s*sr*MeV/nuc)',
                         1 / (u.cm**2 * u.sr * u.MeV * u.s)),
                        ('#/(cm^2*s*sr*Mev/nuc)',
                         1 / (u.cm**2 * u.sr * u.MeV * u.s)),
                        ('1/(cm2 Sr sec MeV/nucleon)',
                         1 / (u.cm**2 * u.sr * u.s * u.MeV)),
                        ('1/(cm**2-s-sr-MeV)',
                         1 / (u.cm**2 * u.s * u.sr * u.MeV)),
                        ('1/(cm**2-s-sr-MeV/nuc.)',
                         1 / (u.cm**2 * u.s * u.sr * u.MeV)),
                        ('1/(cm^2 sec ster MeV)',
                         1 / (u.cm**2 * u.s * u.sr * u.MeV)),
                        ('cnts/sec/sr/cm^2/MeV',
                         1 / (u.cm**2 * u.s * u.sr * u.MeV)),
                        ('particles/(s cm2 sr MeV/n)',
                         1 / (u.cm**2 * u.s * u.sr * u.MeV)),

                        ('1/(cm**2-s-sr)', 1 / (u.cm**2 * u.s * u.sr)),
                        ('1/(SQcm-ster-s)', 1 / (u.cm**2 * u.s * u.sr)),
                        ('1/(SQcm-ster-s)..', 1 / (u.cm**2 * u.s * u.sr)),

                        ('Counts/256sec', 1 / (256 * u.s)),
                         ('Counts/hour', 1 / u.hr),
                        ('cnts/sec', 1 / u.s)
                         ])
    try:
        return units[unit_string]
    except KeyError:
        return None


def _check_in_list(_values, **kwargs):
    """
    For each *key, value* pair in *kwargs*, check that *value* is in *_values*;
    if not, raise an appropriate ValueError.

    Examples
    --------
    >>> cbook._check_in_list(["foo", "bar"], arg=arg, other_arg=other_arg)
    """
    values = _values
    for k, v in kwargs.items():
        if v not in values:
            raise ValueError(
                "{!r} is not a valid value for {}; supported values are {}"
                .format(v, k, ', '.join(map(repr, values))))
