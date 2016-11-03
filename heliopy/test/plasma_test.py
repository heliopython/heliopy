from pyspace.plasma import *
import numpy as np


def test_magneticpressure():
    assert magneticpressure(0) == 0
