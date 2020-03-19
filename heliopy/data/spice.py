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
import requests

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


def _stereo_kernels(probe, type):
    '''
    Probe: 'ahead' or 'behind'
    type: 'epm' or 'depm'
    '''
    if not isinstance(probe, str):
        raise TypeError('argument not of type \'str\'')
    if probe == 'ahead' or probe == 'behind':
        try:
            request = requests.get(
                'https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/{}/{}/'.format(
                    type, probe), timeout=5)
            return ['https://sohowww.nascom.nasa.gov/solarsoft/stereo/gen/data/spice/{}/{}/{}'.format(
                    type, probe, S.split('"')[1])
                    for S in request.text.split('href') if '.bsp' in S]
        except requests.exceptions.ConnectionError:
            return []
    else:
        raise ValueError('argument should be either \'ahead\' or \'behind\'')


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

spacecraft_kernels = [_Kernel('Cassini', 'cassini',
                              ['https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/co_1997288_97318_launch_v1.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/co_1997319_99311_i_cru_v1.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/co_1999312_01066_o_cru_v1.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/041014R_SCPSE_01066_04199.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_04199_04247.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_04247_04336.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_04336_05015.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05015_05034.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05034_05060.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05060_05081.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05081_05097.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05097_05114.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05114_05132.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05132_05150.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05150_05169.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05169_05186.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05186_05205.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05205_05225.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05225_05245.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05245_05257.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05257_05275.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05275_05293.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05293_05320.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05320_05348.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05348_06005.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06005_06036.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06036_06068.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06068_06099.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06099_06130.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06130_06162.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06162_06193.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06193_06217.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06217_06240.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06240_06260.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06260_06276.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06276_06292.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06292_06308.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06308_06318.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06318_06332.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06332_06342.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06342_06356.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_06356_07008.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07008_07023.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07023_07042.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07042_07062.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07062_07077.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07077_07094.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07094_07106.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07106_07125.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07125_07140.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07140_07155.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07155_07170.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07170_07191.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07191_07221.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07221_07262.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07262_07309.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07309_07329.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07329_07345.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07345_07365.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_07365_08045.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08045_08067.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08067_08078.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08078_08126.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08126_08141.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08141_08206.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08206_08220.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08220_08272.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08272_08294.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08294_08319.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08319_08334.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08334_08350.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_08350_09028.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09028_09075.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09075_09089.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09089_09104.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09104_09120.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09120_09136.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09136_09153.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09153_09168.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09168_09184.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09184_09200.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09200_09215.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09215_09231.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09231_09275.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09275_09296.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09296_09317.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09317_09339.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09339_09355.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_09355_10003.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10003_10021.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10021_10055.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10055_10085.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10085_10110.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10110_10132.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10132_10146.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10146_10164.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10164_10178.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10178_10216.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10216_10256.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10256_10302.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10302_10326.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10326_10344.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_10344_11003.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11003_11041.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11041_11093.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11093_11119.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11119_11150.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11150_11246.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11246_11267.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11267_11303.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11303_11337.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11337_11357.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_11357_12016.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12016_12042.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12042_12077.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12077_12098.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12098_12116.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12116_12136.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12136_12151.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12151_12199.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12199_12257.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12257_12304.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12304_12328.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_12328_13038.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13038_13063.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13063_13087.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13087_13137.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13137_13182.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13182_13200.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13200_13241.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13241_13273.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13273_13314.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13314_13352.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_13352_14025.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14025_14051.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14051_14083.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14083_14118.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14118_14156.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14156_14187.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14187_14222.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14222_14251.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14251_14283.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14283_14327.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14327_14365.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_14365_15033.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15033_15066.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15066_15116.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15116_15161.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15161_15180.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15180_15222.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15222_15261.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15261_15280.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15280_15295.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15295_15310.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15310_15347.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_15347_16007.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16007_16025.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16025_16041.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16041_16088.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16088_16115.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16115_16146.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16146_16201.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16201_16217.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16217_16262.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16262_16282.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16282_16310.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16310_16329.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16329_16363.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_16363_17061.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_17061_17104.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_17104_17117.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_17117_17146.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_17146_17177.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_17177_17224.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_17224_17258.bsp'],
                              ''),
                        _Kernel('Cassini_test', 'cassini_test',
                              ['https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_04183_04199.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_04199_04247.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_04247_04336.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_04336_05015.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05015_05034.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05034_05060.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05060_05081.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05081_05097.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05097_05114.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05114_05132.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05132_05150.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05150_05169.bsp',
                                 'https://naif.jpl.nasa.gov/pub/naif/pds/data/co-s_j_e_v-spice-6-v1.0/cosp_1000/data/spk/180628RU_SCPSE_05169_05186.bsp'],
                              ''),
                      _Kernel('Helios 1', 'helios1',
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
                              _stereo_kernels('ahead', 'depm'),
                              ''),
                      _Kernel('STEREO-B', 'stereo_b',
                              _stereo_kernels('behind', 'depm'),
                              ''),
                      _Kernel('SOHO', 'soho',
                              ['https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_1995.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_1996.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_1997.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_1998a.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_1998b.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_1999.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2000.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2001.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2002.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2003.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2004.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2005.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2006.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2007.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2008.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2009.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2010.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2011.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2012.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2013.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2014.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2015.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2016.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2017.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2018.bsp',
                               'https://sohowww.nascom.nasa.gov/sdb/soho/gen/spice/soho_2019.bsp', ],
                              ''),
                      _Kernel('Ulysses', 'ulysses',
                              ['https://naif.jpl.nasa.gov/pub/naif/ULYSSES/kernels/spk/ulysses_1990_2009_2050.bsp',
                               'https://naif.jpl.nasa.gov/pub/naif/ULYSSES/kernels/spk/ulysses_1990_2009_2050.cmt']),
                      _Kernel('Parker Solar Probe', 'psp',
                              ['https://sppgway.jhuapl.edu/MOC/reconstructed_ephemeris/2018/spp_recon_20180812_20181008_v001.bsp',
                               'https://sppgway.jhuapl.edu/MOC/reconstructed_ephemeris/2018/spp_recon_20181008_20190120_v001.bsp',
                               'https://sppgway.jhuapl.edu/MOC/reconstructed_ephemeris/2019/spp_recon_20190120_20190416_v001.bsp',
                               ])]


predicted_kernels = [
    _Kernel('Solar Orbiter 2020', 'solo_2020',
            'https://issues.cosmos.esa.int/solarorbiterwiki/download/attachments/7274724/solo_ANC_soc-orbit_20200207-20300902_V01.bsp'
            ),
    _Kernel('Parker Solar Probe', 'psp_pred',
            ['https://sppgway.jhuapl.edu/MOC/ephemeris//spp_nom_20180812_20250831_v035_RO2.bsp']
            ),
    _Kernel('STEREO-A', 'stereo_a_pred',
            _stereo_kernels('ahead', 'epm'),
            ''),
    _Kernel('STEREO-B', 'stereo_b_pred',
            _stereo_kernels('behind', 'epm'),
            ''),
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
