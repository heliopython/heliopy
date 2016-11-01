from pyspace.plasma import *
from pyspace.constants import *
import numpy as np


def test_magneticpressure():
    assert magneticpressure(0) == 0
