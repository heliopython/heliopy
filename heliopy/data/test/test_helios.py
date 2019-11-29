from datetime import datetime
import pathlib
import shutil
import urllib

import pytest

from .util import check_data_output

helios = pytest.importorskip('heliopy.data.helios')
pytest.mark.data()

probe = '1'


def test_merged():
    starttime = datetime(1976, 1, 10, 0, 0, 0)
    endtime = datetime(1976, 1, 10, 23, 59, 59)
    df = helios.merged(probe, starttime, endtime)
    check_data_output(df)

    starttime = datetime(2000, 1, 1, 0, 0, 0)
    endtime = datetime(2000, 1, 2, 0, 0, 0)
    with pytest.raises(RuntimeError):
        helios.merged(probe, starttime, endtime)


def test_corefit():
    starttime = datetime(1976, 1, 10, 0, 0, 0)
    endtime = datetime(1976, 1, 10, 23, 59, 59)
    df = helios.corefit(probe, starttime, endtime)
    check_data_output(df)

    starttime = datetime(2000, 1, 1, 0, 0, 0)
    endtime = datetime(2000, 1, 2, 0, 0, 0)
    with pytest.raises(RuntimeError):
        helios.corefit(probe, starttime, endtime)


def test_6sec_ness():
    starttime = datetime(1976, 1, 16)
    endtime = datetime(1976, 1, 18)
    probe = '2'
    df = helios.mag_ness(probe, starttime, endtime)
    check_data_output(df)


def test_distribution_funcs():
    local_dir = pathlib.Path(helios.helios_dir)
    local_dir = local_dir / 'helios1' / 'dist' / '1974' / '346'
    local_dir.mkdir(parents=True, exist_ok=True)
    remote_file = ('http://helios-data.ssl.berkeley.edu/data/E1_experiment'
                   '/helios_original/helios_1/1974/346/'
                   'h1y74d346h03m27s21_hdm.1')
    local_fname, _ = urllib.request.urlretrieve(
        remote_file, './h1y74d346h03m27s21_hdm.1')
    local_fname = pathlib.Path(local_fname)
    new_path = local_dir / local_fname.name
    shutil.copyfile(local_fname, new_path)

    helios.integrated_dists(
        '1', datetime(1974, 12, 12), datetime(1974, 12, 13))

    helios.distparams(
        '1', datetime(1974, 12, 12), datetime(1974, 12, 13))

    helios.electron_dists(
        '1', datetime(1974, 12, 12), datetime(1974, 12, 13))

    helios.ion_dists(
        '1', datetime(1974, 12, 12), datetime(1974, 12, 13))


def test_mag_4hz():
    starttime = datetime(1976, 1, 16)
    endtime = datetime(1976, 1, 18)
    probe = '2'
    df = helios.mag_4hz(probe, starttime, endtime)
    check_data_output(df)
