import heliopy.stats as heliostats
import numpy as np
import matplotlib.pyplot as plt

# Create a theta, phi grid
theta = np.linspace(-np.pi / 2, np.pi / 2, 50)
phi = np.linspace(-np.pi, np.pi, 100)
theta, phi = np.meshgrid(theta, phi)

kappa = 2
beta = 0.5
theta_0 = 0
phi_0 = 0
theta_1s = [0, 1]
phi_1s = [1, 0]

# Plot two different distributions
fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
for ax, theta_1, phi_1 in zip(axs, theta_1s, phi_1s):
    dist = heliostats.kent_dist(theta, phi, kappa, beta,
                                theta_0, phi_0, theta_1, phi_1)

    ax.scatter(phi, theta, c=dist)
    ax.scatter(phi_1, theta_1, color='r')

# Plot formatting
axs[0].set_xlim((-np.pi, np.pi))
axs[0].set_ylim((-np.pi / 2, np.pi / 2))
axs[1].set_xlabel('phi')
axs[1].set_ylabel('theta')

axs[0].set_title('Stretched along phi')
axs[1].set_title('Stretched along theta')

plt.show()
