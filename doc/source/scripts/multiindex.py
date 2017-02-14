import pandas as pd
import numpy as np

# Energy bins
E = np.arange(0, 4)
# Azimuthal angles
phi = np.arange(0, 360, 90)
# Elevation angles
theta = np.arange(-90, 90, 45)
# Fake distribution function
dist = np.random.rand(E.size * phi.size * theta.size)

index = pd.MultiIndex.from_product((E, theta, phi),
                                   names=('E', 'theta', 'phi'))
data = pd.DataFrame(data=dist, index=index, columns=['df'])
print(data.head())
"""
                   df
E theta phi
0 -90   0    0.369417
        90   0.074464
        180  0.470669
        270  0.320014
  -45   0    0.607422
"""

for theta, theta_data in data.groupby(level='theta'):
    print(theta)
"""
-90
-45
0
45
"""
