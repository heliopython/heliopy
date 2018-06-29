![HelioPy](https://github.com/heliopython/heliopy/raw/master/artwork/logo_rectangle.png "HelioPy")

A python library for heliospheric and planetary Physics.
The primary goal of HelioPy is to provide a set of tools to download and read
in data, and to carry out other common data processing tasks.

Full documentation can be found [here](http://docs.heliopy.org/).

A quick example shows how easy it is to import and view data:

```python
from datetime import datetime, timedelta
import heliopy.data.wind as wind
import matplotlib.pyplot as plt

starttime = datetime(2016, 1, 1, 0, 0, 0)
endtime = starttime + timedelta(hours=2)

data = wind.mfi_h0(starttime, endtime)

plt.plot(data['Bx_gse'])
plt.plot(data['By_gse'])
plt.plot(data['Bz_gse'])

plt.show()
```

**If HelioPy is missing a method to import a dataset you are interested in,
please submit a request at https://github.com/heliopython/heliopy/issues.**


[![Build Status](https://travis-ci.org/heliopython/heliopy.svg?branch=master)](https://travis-ci.org/heliopython/heliopy)
[![Coverage](https://codecov.io/gh/heliopython/heliopy/branch/master/graph/badge.svg)](https://codecov.io/gh/heliopython/heliopy)
