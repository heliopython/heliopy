"""
SPICE
=====
Methods for automatically downloading SPICE kernels for various objects.
This is essentially a library of SPICE kernels that are available online, so
users don't have go go hunting for them. If you know a kernel is out of date,
and HelioPy should be using a newer kernel please let us know at
https://github.com/heliopython/heliopy/issues.

"""
import os
import warnings

from urllib.request import urlretrieve
import urllib.error

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
                   _Kernel('Planet trajectories', 'planet_trajectories',
                           'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp',
                           'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/aa_summaries.txt'),
                   _Kernel('Planet orientations', 'planet_orientations',
                           'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00010.tpc',
                           'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/aareadme.txt'),
                   _Kernel('Heliospheric frames', 'helio_frames',
                           'https://naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/fk/heliospheric_v004u.tf'),
                   ]

spacecraft_kernels = [_Kernel('Helios 1', 'helios1',
                              ['https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/100528R_helios1_74345_81272.bsp',
                               'https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/160707AP_helios1_81272_86074.bsp'
                               ],
                              'https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/aareadme_kernel_construction.txt'
                              ),
                      _Kernel('Helios 2', 'helios2',
                              'https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/100607R_helios2_76016_80068.bsp',
                              'https://naif.jpl.nasa.gov/pub/naif/HELIOS/kernels/spk/aareadme_kernel_construction.txt'),
                      _Kernel('Juno', 'juno',
                              'https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/juno_rec_orbit.bsp',
                              'https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/aareadme.txt'),
                      _Kernel('STEREO-A', 'stereo_a',
                              ['https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2006_350_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2008_037_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2008_078_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2010_208_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2012_138_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2013_130_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2015_076_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2015_219_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2018_019_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2019_030_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2019_045_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2019_060_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2019_063_01.depm.bsp',
                               'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/depm/ahead/ahead_2019_080_01.depm.bsp', ],
                              ''),
                      _Kernel('Ulysses', 'ulysses',
                              ['https://naif.jpl.nasa.gov/pub/naif/ULYSSES/kernels/spk/ulysses_1990_2009_2050.bsp',
                               'https://naif.jpl.nasa.gov/pub/naif/ULYSSES/kernels/spk/ulysses_1990_2009_2050.cmt']),
                      _Kernel('Parker Solar Probe', 'psp',
                              ['https://sppgway.jhuapl.edu/MOC/reconstructed_ephemeris/2018/spp_recon_20180812_20181008_v001.bsp',
                               ])]


predicted_kernels = [
    _Kernel('Solar Orbiter 2020', 'solo_2020',
            'https://issues.cosmos.esa.int/solarorbiterwiki/download/attachments/7274724/solo_ANC_soc-orbit_20200207-20300902_V01.bsp'
            ),
    _Kernel('Parker Solar Probe', 'psp_pred',
            ['https://sppgway.jhuapl.edu/MOC/ephemeris//spp_nom_20180812_20250831_v035_RO2.bsp']
            ),
    _Kernel('STEREO-A', 'stereo_a_pred',
            ['https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/epm/ahead/ahead_2017_061_5295day_predict.epm.bsp']
            ),
    _Kernel('Juno Predicted', 'juno_pred',
            'https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/juno_pred_orbit.bsp',
            'https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/spk/aareadme.txt'
            ),
    _Kernel('Bepi-Columbo', 'bepi_pred',
            'ftp://spiftp.esac.esa.int/data/SPICE/BEPICOLOMBO/kernels/spk/bc_mpo_fcp_00046_20181020_20251102_v01.bsp',
            'https://repos.cosmos.esa.int/socci/projects/SPICE_KERNELS/repos/bepicolombo/browse/kernels/spk/aareadme.txt'),
]


kernel_dict = {}
for kernel in generic_kernels + spacecraft_kernels + predicted_kernels:
    kernel_dict[kernel.short_name] = kernel


def get_kernel(name):
    """
    Get the local location of a kernel.

    If a kernel isn't available locally, it is downloaded.

    Parameters
    ----------
    name : str
        Kernel name. See :ref:`data_spice_generic_kernels` and
        :ref:`data_spice_spacecraft_kernels` for lists of
        available names. The name should be a string from the "Identifier"
        column of one of the tables.

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
        fname = url[url.rfind("/") + 1:]
        local_loc = os.path.join(spice_dir, fname)
        locs.append(local_loc)
        if not os.path.exists(spice_dir):
            os.makedirs(spice_dir)
        if not os.path.exists(local_loc):
            print('Downloading {}'.format(url))
            try:
                urlretrieve(url, local_loc, reporthook=util._reporthook)
            except urllib.error.HTTPError as err:
                warnings.warn('Failed to download {}'.format(url))
    return locs


# End of main code, now create tables for spice kernels

__doc__ += '''

Generic kernels
---------------
These are general purpose kernels, used for most caclulations. They are all
automatically loaded if you are using the :mod:`heliopy.spice` module.

.. csv-table:: Generic kernels
   :name: data_spice_generic_kernels
   :header: "Name", "Identifier", "Kernel URL(s)"
   :widths: 30, 20, 30
'''
for kernel in generic_kernels:
    __doc__ += kernel.make_doc_entry()

# Documentation for reconstructed trajectories
__doc__ += '''

Actual trajectories
-------------------
These kernels store the actual trajectory of a body.

.. csv-table:: Reconstructed kernels
   :name: data_spice_spacecraft_kernels
   :header: "Name", "Identifier", "Kernel URL(s)"
   :widths: 30, 20, 30
'''

for kernel in (sorted(spacecraft_kernels, key=lambda x: x.short_name)):
    __doc__ += kernel.make_doc_entry()

# Documentation for predicted trajectories
__doc__ += '''

Predicted trajectories
----------------------
These kernels store the predicted trajectory of a body.

.. warning::

    No guarentee is given as to the reliability of these kernels. Newer
    predicted trajectories may be available, or newer reconstructued
    (ie. actual) trajectory files may also be available.

    Use at your own risk!

.. csv-table:: Predicted kernels
   :name: data_spice_predicted_kernels
   :header: "Name", "Identifier", "Kernel URL(s)"
   :widths: 30, 20, 30
'''

for kernel in (sorted(predicted_kernels, key=lambda x: x.short_name)):
    __doc__ += kernel.make_doc_entry()
