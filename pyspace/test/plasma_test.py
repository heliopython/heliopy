from pyspace.plasma import *
from pyspace.constants import *
import numpy as np


def test_magneticpressure():
    assert magneticpressure(0) == 0
    assert magneticpressure(1e9 * np.sqrt(k_B * 2)) == 1.0
