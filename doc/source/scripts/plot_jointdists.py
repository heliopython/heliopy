from datetime import datetime
import matplotlib.pyplot as plt

import heliopy.plot.fields as pltfields
import heliopy.data.wind as wind

starttime = datetime(2003, 5, 15, 0, 0, 0)
endtime = datetime(2003, 5, 16, 0, 0, 0)
mag = wind.mfi_h0(starttime, endtime)

pltfields.jointdists(mag[['Bx_gse', 'By_gse', 'Bz_gse']])
plt.show()
