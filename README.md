# heliopy

A python library for Space Physics. The primary goal of this python package is
to make it really easy to import common data sets used in Space Physics.

A quick example shows how easy it is to import and view data:

```
from datetime import datetime, timedelta
import heliopy.data.wind as wind
import matplotlib.pyplot as plt

starttime = datetime(2016, 1, 1, 0, 0, 0)
endtime = starttime + timedelta(hours=2)

data = wind.mfi_h0(starttime, endtime)

print(data.keys())
# Index(['Bx', 'By', 'Bz', 'Br', 'Time'], dtype='object')

plt.plot(data['Time'], data['Bx_gse'])
plt.plot(data['Time'], data['By_gse'])
plt.plot(data['Time'], data['Bz_gse'])
plt.show()
```

If heliopy is missing a method to import a dataset you are interested in, please
submit a request at https://github.com/heliopython/heliopy/issues.

Full documentation can be found [here](http://heliopy.readthedocs.io/en/latest/).

[![Build Status](https://travis-ci.org/heliopython/heliopy.svg?branch=master)](https://travis-ci.org/heliopython/heliopy)
[![Code Health](https://landscape.io/github/heliopython/heliopy/master/landscape.svg?style=flat)](https://landscape.io/github/heliopython/heliopy/master)
[![Coverage Status](https://coveralls.io/repos/github/heliopython/heliopy/badge.svg?branch=master)](https://coveralls.io/github/heliopython/heliopy?branch=master)
