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
import heliopy.data.util as util

data_dir = config['download_dir']
spice_dir = os.path.join(data_dir, 'spice')


class _Kernel:
    def __init__(self, name, short_name, urls, readme_link=''):
        self.name = name
        self.short_name = short_name
        if isinstance(urls, str):
            urls = [urls]
        self.urls = urls
        self.readme_link = readme_link

    def make_doc_entry(self):
        url_doc = ''
        for i, url in enumerate(self.urls):
            url_doc += '`[{}] <{}>`__ '.format(i + 1, url)

        if len(self.readme_link):
            name_doc = '`{} <{}>`_'.format(self.name, self.readme_link)
        else:
            name_doc = self.name
        return '\n   {}, {}, {}'.format(
            name_doc, self.short_name, url_doc)


generic_kernels = [_Kernel('Leap Second Kernel', 'lsk',
                           'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls'),
                   _Kernel('Development Ephemeris', 'planets',
                           'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp')]

spacecraft_kernels = [_Kernel('Solar Orbiter 2020', 'solo_2020',
                              'https://issues.cosmos.esa.int/solarorbiterwiki/download/attachments/7274724/solo_ANC_soc-orbit_20200207-20300902_V01.bsp'),
                      _Kernel('Helios 1', 'helios1',
                              ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/100528R_helios1_74345_81272.bsp',
                               'https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/160707AP_helios1_81272_86074.bsp'],
                              'https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/aareadme_kernel_construction.txt'),
                      _Kernel('Helios 2', 'helios2',
                              'https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/100607R_helios2_76016_80068.bsp',
                              'https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/aareadme_kernel_construction.txt'),
                      _Kernel('Juno reconstructed', 'juno_rec',
                              'https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/juno_rec_orbit.bsp',
                              'https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/aareadme.txt'),
                      _Kernel('Juno predicted', 'juno_pred',
                              'https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/juno_pred_orbit.bsp',
                              'https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/aareadme.txt')
                      ]

kernel_dict = {}
for kernel in generic_kernels + spacecraft_kernels:
    kernel_dict[kernel.name] = kernel

__doc__ += '''
.. csv-table:: Generic kernels
   :name: data_spice_generic_kernels
   :header: "Name", "Identifier", "Kernel URL(s)"
   :widths: 30, 20, 30
'''
for kernel in generic_kernels:
    __doc__ += kernel.make_doc_entry()

__doc__ += '''
.. csv-table:: Spacecraft kernels
   :name: data_spice_spacecraft_kernels
   :header: "Name", "Identifier", "Kernel URL(s)"
   :widths: 30, 20, 30
'''
for kernel in spacecraft_kernels:
    __doc__ += kernel.make_doc_entry()
# Kernel Download Sources
'''for kernel in sorted(available_kernels):
    __doc__ += '\n   {}, {}, {}, '.format(
        kernel_name[kernel][0], kernel, kernel_readme[kernel][0])
    for url in available_kernels[kernel]:
        __doc__ += '{} '.format(url)'''


def get_kernel(name):
    """
    Get the local location of a kernel.

    If a kernel isn't available locally, it is downloaded.

    Parameters
    ----------
    name : str
        Kernel name. See :ref:`data_spice_generic_kernels` for a list of
        available names.

    Returns
    -------
    list
        List of the locations of kernels that have been downloaded.
    """
    if name not in kernel_dict:
        raise ValueError(
            'Provided name {} not in list of available names: {}'.format(
                name, kernel_dict.keys()))
    kernel = kernel_dict[name]
    locs = []
    for url in kernel.urls:
        fname = url[url.rfind("/")+1:]
        local_loc = os.path.join(spice_dir, fname)
        locs.append(local_loc)
        if not os.path.exists(spice_dir):
            os.makedirs(spice_dir)
        if not os.path.exists(local_loc):
            print('Downloading {}'.format(url))
            urlretrieve(url, local_loc, reporthook=util._reporthook)
    return locs
