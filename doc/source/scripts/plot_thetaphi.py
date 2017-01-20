from datetime import datetime
import matplotlib.pyplot as plt

import heliopy.plot.fields as pltfields
import heliopy.data.wind as wind

starttime = datetime(2003, 5, 15, 0, 0, 0)
endtime = datetime(2003, 5, 16, 0, 0, 0)
mag = wind.mfi_h0(starttime, endtime)

pltfields.thetaphi(mag['Bx_gse'], mag['By_gse'], mag['Bz_gse'])
plt.show()
