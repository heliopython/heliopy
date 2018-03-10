"""
SPICE
-----
Methods for automatically downloading SPICE kernels for various objects.
This is essentially a library of SPICE kernels that are available online, so
users don't have go go hunting for them. If you know a kernel is out of date,
and HelioPy should be using a newer kernel please let us know at
https://github.com/heliopython/heliopy/issues.
To fetch a kernel, use the kernel identifier in the brackets.

.. csv-table:: Available kernels
   :name: data_spice_kernels
   :header: "Name(Identifier)", "Readme", "URL(s)"
   :widths: 30, 70, 70
"""
import os
from urllib.request import urlretrieve

from heliopy import config
import heliopy.data.util as util

data_dir = config['download_dir']
spice_dir = os.path.join(data_dir, 'spice')
# Mapping of kernel name to remote location
kernel_name = {'lsk': ['Leap Second Kernel'],
               'planets': ['Development Ephemeris'],
               'solar orbiter 2020': ['Solar Orbiter 2020'],
               'helios1_rec': ['Helios 1 Reconstructed'],
               'helios1_pred': ['Helios 1 Predicted'],
               'helios2': ['Helios 2'],
               'juno_rec': ['Juno Reconstructed'],
               'juno_pred': ['Juno Predicted'],
               'clem_nrl': ['Clementine-Naval Research Laboratory'],
               'clem_gsfc': ['Clementine-Goddard Space Flight Center'],
               'clem_jpl': ['Clementine-Jet Propulsion Laboratory'],
               'deepimpact_adjusted': ['Deep Impact-Adjusted'],
               'deepimpact_original': ['Deep Impact-Original'],
               'deepimpact_complete': ['Deep Impact-Complete'],
               'deepspace': ['Deep Space'],
               'epoxi_dixi': ['EPOXI-DIXI'],
               'epoxi_epoch': ['EPOXI-ePOCh'],
               'hayabusa_complete': ['Hayabusa-Complete']}
# Kernel Names
kernel_readme = {'lsk': [''],
                 'planets': [''],
                 'solar orbiter 2020': [''],
                 'helios1_rec': ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/aareadme_kernel_construction.txt'],
                 'helios1_pred': ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/aareadme_kernel_construction.txt'],
                 'helios2': ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/aareadme_kernel_construction.txt'],
                 'juno_rec': ['https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/aareadme.txt'],
                 'juno_pred': ['https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/aareadme.txt'],
                 'clem_nrl': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/clem1-l-spice-6-v1.0/clsp_1000/data/spk/spkinfo.txt'],
                 'clem_gsfc': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/clem1-l-spice-6-v1.0/clsp_1000/data/spk/spkinfo.txt'],
                 'clem_jpl': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/clem1-l-spice-6-v1.0/clsp_1000/data/spk/spkinfo.txt'],
                 'deepimpact_adjusted': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/di-c-spice-6-v1.0/disp_1000/data/spk/spkinfo.txt'],
                 'deepimpact_original': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/di-c-spice-6-v1.0/disp_1000/data/spk/spkinfo.txt'],
                 'deepimpact_complete': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/di-c-spice-6-v1.0/disp_1000/data/spk/spkinfo.txt'],
                 'deepspace': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/ds1-a_c-spice-6-v1.0/ds1sp_1000/data/spk/spkinfo.txt'],
                 'epoxi_dixi': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/dif-c_e_x-spice-6-v1.0/epxsp_1000/data/spk/spkinfo.txt'],
                 'epoxi_epoch': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/dif-c_e_x-spice-6-v1.0/epxsp_1000/data/spk/spkinfo.txt'],
                 'hayabusa_complete': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/hay-a-spice-6-v1.0/haysp_1000/data/spk/spkinfo.txt']}
# Kernel Readme(s)
available_kernels = {'lsk': ['https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls'],
                     'planets': ['https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp'],
                     'solar orbiter 2020': ['https://issues.cosmos.esa.int/solarorbiterwiki/download/attachments/7274724/solo_ANC_soc-orbit_20200207-20300902_V01.bsp'],
                     'helios1_rec': ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/100528R_helios1_74345_81272.bsp'],
                     'helios1_pred': ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/160707AP_helios1_81272_86074.bsp'],
                     'helios2': ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/100607R_helios2_76016_80068.bsp'],
                     'juno_rec': ['https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/juno_rec_orbit.bsp'],
                     'juno_pred': ['https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/juno_pred_orbit.bsp'],
                     'clem_nrl': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/clem1-l-spice-6-v1.0/clsp_1000/data/spk/clem_nrl.bsp'],
                     'clem_gsfc': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/clem1-l-spice-6-v1.0/clsp_1000/data/spk/clem_gsfc.bsp'],
                     'clem_jpl': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/clem1-l-spice-6-v1.0/clsp_1000/data/spk/clem_jpl.bsp'],
                     'deepimpact_adjusted': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/di-c-spice-6-v1.0/disp_1000/data/spk/di_finalenc_nav_v3_to06048.bsp'],
                     'deepimpact_original': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/di-c-spice-6-v1.0/disp_1000/data/spk/di_finalenc_nav_v3.bsp'],
                     'deepimpact_complete': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/di-c-spice-6-v1.0/disp_1000/data/spk/dii_preenc174_nav_v1.bsp', 'https://naif.jpl.nasa.gov/pub/naif/pds/data/di-c-spice-6-v1.0/disp_1000/data/spk/dif_preenc174_nav_v1.bsp', 'https://naif.jpl.nasa.gov/pub/naif/pds/data/di-c-spice-6-v1.0/disp_1000/data/spk/di_tempel1_ssd_v1.bsp', 'https://naif.jpl.nasa.gov/pub/naif/pds/data/di-c-spice-6-v1.0/disp_1000/data/spk/di_finalenc_nav_v3_to06048.bsp'],
                     'deepspace': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/ds1-a_c-spice-6-v1.0/ds1sp_1000/data/spk/ds1_radionav.bsp'],
                     'epoxi_dixi': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/dif-c_e_x-spice-6-v1.0/epxsp_1000/data/spk/dif_dixi_nav_v1.bsp'],
                     'epoxi_epoch': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/dif-c_e_x-spice-6-v1.0/epxsp_1000/data/spk/dif_epoch_nav_v1.bsp'],
                     'hayabusa_complete': ['https://naif.jpl.nasa.gov/pub/naif/pds/data/hay-a-spice-6-v1.0/haysp_1000/data/spk/de403s.bsp', 'https://naif.jpl.nasa.gov/pub/naif/pds/data/hay-a-spice-6-v1.0/haysp_1000/data/spk/sb_25143_140.bsp', 'https://naif.jpl.nasa.gov/pub/naif/pds/data/hay-a-spice-6-v1.0/haysp_1000/data/spk/hay_jaxa_050916_051119_v1n.bsp', 'https://naif.jpl.nasa.gov/pub/naif/pds/data/hay-a-spice-6-v1.0/haysp_1000/data/spk/hay_osbj_050911_051118_v1n.bsp']}
# Kernel Download Sources
for kernel in available_kernels:
    __doc__ += '\n   {}({}), {}, '.format(kernel_name[kernel], kernel, kernel_readme[kernel])
    for url in available_kernels[kernel]:
        __doc__ += '{} '.format(url)


def get_kernel(name):
    """
    Get the local location of a kernel.
    If a kernel isn't available locally, it is downloaded.
    Parameters
    ----------
    name : str
        Kernel name. See PUT LINK HERE for a list of available names.
    Returns
    -------
    list
        List of the locations of kernels that have been downloaded.
    """
    if name not in available_kernels:
        raise ValueError(
            'Provided name {} not in list of supported names: {}'.format(
                name, list(available_kernels.keys())))
    locs = []
    for url in available_kernels[name]:
        fname = url.split('/')[-1]
        local_loc = os.path.join(spice_dir, kernel_name[name][0], fname)
        locs.append(local_loc)
        if not os.path.exists(os.path.join(spice_dir, kernel_name[name][0])):
            os.makedirs(os.path.join(spice_dir, kernel_name[name][0]))
        if not os.path.exists(local_loc):
            print('Downloading {}'.format(url))
            urlretrieve(url, local_loc, reporthook=util._reporthook)
    return locs
