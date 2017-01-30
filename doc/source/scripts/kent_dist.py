import heliopy.stats as heliostats
import numpy as np
import matplotlib.pyplot as plt

# Create a theta, phi grid
theta = np.linspace(-np.pi / 2, np.pi / 2, 100)
phi = np.linspace(-np.pi, np.pi, 100)
theta, phi = np.meshgrid(theta, phi)

# Create two distributions, centred on (0, 0)
wide_dist = heliostats.kent_dist(theta, phi, 3, 1, 0, 0, 0, np.pi / 2)
narrow_dist = heliostats.kent_dist(theta, phi, 3, 1, 0, 0, 0.1, 0)

# Plot the distributions
fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
axs[0].scatter(phi, theta, c=wide_dist)
axs[1].scatter(phi, theta, c=narrow_dist)

# Plot formatting
axs[0].set_xlim((-np.pi, np.pi))
axs[0].set_ylim((-np.pi / 2, np.pi / 2))
axs[1].set_xlabel('phi')
axs[1].set_ylabel('theta')

axs[0].set_title('kappa = 1')
axs[1].set_title('kappa = 5')

plt.show()
