'''
Statistical methods
'''
import numpy as np


def hist(x, bins='auto', normed=True, return_centres=True):
    '''
    Improved histogram function
    '''
    hist, bin_edges = np.histogram(x, bins=bins, normed=normed)
    # Calculate centres of bins (e.g. for plotting scatter pdf)
    bin_centres = (bin_edges[1:] + bin_edges[:-1]) / 2
    if return_centres:
        return hist, bin_centres
    else:
        return hist, bin_edges
