import matplotlib.pyplot as plt
import numpy as np


def scatter3D(x, y, z, pdf):
    '''
    Perform 3D scatter plot of distribution function data
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c=np.log10(pdf), s=40)
