from datetime import datetime, timedelta
import heliopy.data.wind as wind
import matplotlib.pyplot as plt

starttime = datetime(2016, 1, 1, 0, 0, 0)
endtime = starttime + timedelta(hours=2)

data = wind.mfi_h0(starttime, endtime)

print(data.keys())
# Index(['Bx', 'By', 'Bz', 'Br', dtype='object')

plt.plot(data['Bx_gse'], label=r'$B_{x}$')
plt.plot(data['By_gse'], label=r'$B_{y}$')
plt.plot(data['Bz_gse'], label=r'$B_{z}$')
plt.legend()
plt.show()
