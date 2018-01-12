"""
SPICE
-----

Methods for automatically downloading SPICE kernels for various objects.

This is essentially a library of SPICE kernels that are available online, so
users don't have go go hunting for them. If you know a kernel is out of date,
and HelioPy should be using a newer kernel please let us know at
https://github.com/heliopython/heliopy/issues.
"""
import os
from urllib.request import urlretrieve

from heliopy import config
import heliopy.data.helper as helper

data_dir = config['download_dir']
spice_dir = os.path.join(data_dir, 'spice')
# Mapping of kernel name to remote location
available_kernels = {'lsk': 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls',
                     'planets': 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de432s.bsp',
                     'solar orbiter 2020': 'https://issues.cosmos.esa.int/solarorbiterwiki/download/attachments/7274724/solo_ANC_soc-orbit_20200207-20300902_V01.bsp'}


def get_kernel(name):
    """
    Get the local location of a kernel.

    If a kernel isn't available locally, it is download.

    Parameters
    ----------
    name : str
        Kernel name. See PUT LINK HERE for a list of available names.

    Returns
    -------
    str
        Local location of kernel.
    """
    if name not in available_kernels:
        raise ValueError(
            'Provided name {} not in list of supported names: {}'.format(
                name, available_kernels))
    url = available_kernels[name]
    fname = url.split('/')[-1]
    local_loc = os.path.join(spice_dir, fname)
    if not os.path.exists(spice_dir):
        os.makedirs(spice_dir)
    if not os.path.exists(local_loc):
        print('Downloading {}'.format(url))
        urlretrieve(url, local_loc, reporthook=helper._reporthook)
    return local_loc
