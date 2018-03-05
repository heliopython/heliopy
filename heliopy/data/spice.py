"""
SPICE
-----

Methods for automatically downloading SPICE kernels for various objects.

This is essentially a library of SPICE kernels that are available online, so
users don't have go go hunting for them. If you know a kernel is out of date,
and HelioPy should be using a newer kernel please let us know at
https://github.com/heliopython/heliopy/issues.

.. csv-table:: Available kernels
   :name: data_spice_kernels
   :header: "Name", "URL(s)"
   :widths: 30, 70

"""
import os
from urllib.request import urlretrieve

from heliopy import config
import heliopy.data.util as util

data_dir = config['download_dir']
spice_dir = os.path.join(data_dir, 'spice')
# Mapping of kernel name to remote location
available_kernels = {'lsk': ['https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls'],
                     'planets': ['https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp'],
                     'solar orbiter 2020': ['https://issues.cosmos.esa.int/solarorbiterwiki/download/attachments/7274724/solo_ANC_soc-orbit_20200207-20300902_V01.bsp'],
                     'Helios 1_Reconstructed': ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/100528R_helios1_74345_81272.bsp'],
                     'Helios 1_Predicted': ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/160707AP_helios1_81272_86074.bsp'],
                     'Helios 2': ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/100607R_helios2_76016_80068.bsp'],
                     'Juno_Reconstructed': ['https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/juno_rec_orbit.bsp'],
                     'Juno_Predicted': ['https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/juno_pred_orbit.bsp']}


for kernel in available_kernels:
    __doc__ += '\n   {}, '.format(kernel)
    for url in available_kernels[kernel]:
        __doc__ += '{} '.format(url)


def get_kernel(name):
    """
    Get the local location of a kernel.

    If a kernel isn't available locally, it is downloaded.

    Parameters
    ----------
    name : str
        Kernel name. See :ref:`data_spice_kernels` for a list of
        available names.

    Returns
    -------
    list
        List of the locations of kernels that have been downloaded.
    """
    if name not in available_kernels:
        raise ValueError(
            'Provided name {} not in list of supported names: {}'.format(
                name, available_kernels))
    locs = []
    for url in available_kernels[name]:
        fname = url.split('/')[-1]
        local_loc = os.path.join(spice_dir, fname)
        locs.append(local_loc)
        if not os.path.exists(spice_dir):
            os.makedirs(spice_dir)
        if not os.path.exists(local_loc):
            print('Downloading {}'.format(url))
            urlretrieve(url, local_loc, reporthook=util._reporthook)
    return locs
