"""
Voyager
=======
Plotting Voyager magnetic field and plasma data.
"""

###############################################################################
# Import the required packages
from heliopy.data import voyager
from datetime import datetime
import matplotlib.pyplot as plt

###############################################################################
# Download and load the merged dataset for a single year
starttime = datetime(1980, 1, 1)
endtime = datetime(1980, 12, 30)
data = voyager.voyager1_merged(starttime, endtime)
print(data.columns)

###############################################################################
# Plot the data
fig, axs = plt.subplots(nrows=2, figsize=(10, 4), sharex=True)

ax = axs[0]
for var in ['BR', 'BT', 'BN']:
    ax.plot(data.index, data.quantity(var), label=var)
ax.set_ylabel('nT')

ax = axs[1]
ax.plot(data.index, data.quantity('V'))
ax.set_ylabel('Velocity (km/s)')

fig.autofmt_xdate()
plt.show()
