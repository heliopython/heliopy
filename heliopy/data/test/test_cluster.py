from datetime import datetime
import pytest

from heliopy import config
from .util import check_data_output

cluster = pytest.importorskip('heliopy.data.cluster')
pytest.mark.data()
if config['cluster_cookie'] == 'none':
    pytesk.skip('Cluster download cookie not set', allow_module_level=True)

probe = '3'


def test_fgm():
    starttime = datetime(2004, 6, 18, 11, 35, 0)
    endtime = datetime(2004, 6, 19, 18, 35, 0)
    df = cluster.fgm(probe, starttime, endtime)
    check_data_output(df)


def test_peace_moments():
    starttime = datetime(2009, 12, 22, 4, 0, 0)
    endtime = datetime(2009, 12, 22, 6)
    df = cluster.peace_moments(probe, starttime, endtime)
    check_data_output(df)


def test_cis_hia_onboard_moms():
    starttime = datetime(2009, 1, 1, 0, 0, 0)
    endtime = datetime(2009, 1, 1, 2, 0, 0)
    df = cluster.cis_hia_onboard_moms(probe, starttime, endtime)
    check_data_output(df)


def test_cis_codif_h1_moms():
    starttime = datetime(2009, 1, 1, 0, 0, 0)
    endtime = datetime(2009, 1, 1, 2, 0, 0)
    df = cluster.cis_codif_h1_moms(probe, starttime, endtime)
    check_data_output(df)
