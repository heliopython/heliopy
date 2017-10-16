# heliopy

A python library for Space Physics. The primary goal of this python package is
to make it really easy to import common data sets used in Space Physics.
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

**If heliopy is missing a method to import a dataset you are interested in,
please submit a request at https://github.com/heliopython/heliopy/issues.**


[![Build Status](https://travis-ci.org/heliopython/heliopy.svg?branch=master)](https://travis-ci.org/heliopython/heliopy)
[![Coverage](https://codecov.io/gh/heliopython/heliopy/branch/master/graph/badge.svg)](https://codecov.io/gh/heliopython/heliopy)
