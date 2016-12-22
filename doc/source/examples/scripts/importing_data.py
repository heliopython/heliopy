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
