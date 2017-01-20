import numpy as np
import matplotlib.pyplot as plt
import heliopy.plot.spectra as specplot

f = np.arange(100) + 1
power = f ** (-5 / 3)

specplot.loglog(f, power, xlabel='Frequency', ylabel='Power')

plt.show()
