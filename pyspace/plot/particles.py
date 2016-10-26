import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


def scatter3D(x, y, z, pdf):
    '''
    Perform 3D scatter plot of distribution function data
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c=np.log10(pdf), s=40)


def contour2D(x, y, pdf, showbins=True):
    '''
    Do a countour plot of 2D distribution function data
    '''
    fig = plt.figure()
    ax = plt.subplot()
    ax.tricontourf(x, y, np.log10(pdf), cmap='viridis', linewidths='1')
    if showbins:
        ax.scatter(x, y, c=np.log10(pdf), cmap='viridis', s=40)


def surf2D(x, y, pdf):
    '''
    3D surf plot of 2D distribution function
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(x, y, np.log10(pdf), cmap='viridis', linewidths=0, alpha=0.5)
