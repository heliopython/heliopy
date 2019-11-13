"""
Parker Solar Probe peihelion 1
==============================

This example shows how to plot magnetic field data from the first perihelion
pass of Parker Solar Probe. Not shown here (because the files are quite large!)
are the particle properties measured by SWEAP, which can be accessed with
`heliopy.data.psp.sweap_spc_l3`.
"""

###############################################################################
# Import the required packages
from heliopy.data import psp
from datetime import datetime
import matplotlib.pyplot as plt

###############################################################################
# Define the starttime and endtime of the perihelion pass
starttime = datetime(2018, 11, 2)
endtime = datetime(2018, 11, 10)

###############################################################################
# Download and load the magnetic field data
mag = psp.fields_mag_rtn_1min(starttime, endtime)

###############################################################################
# Plot the data!
fig, ax = plt.subplots(figsize=(10, 4))

for comp, label in enumerate(['Br', 'Bt', 'Bn']):
    ax.plot(mag.index, mag.quantity(f'psp_fld_l2_mag_RTN_1min_{comp}'),
            linewidth=1, zorder=-comp, label=label)

ax.legend()
ax.set_ylabel('nT')
ax.set_title('PSP Perihelion 1')
fig.autofmt_xdate()
plt.show()
