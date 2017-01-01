"""Methods for plotting different types of spectra."""
import matplotlib.pyplot as plt


def loglog(fs, power, title=None, xlabel=r'$f /Hz$', ylabel='', legend=None,
           ax=None):
    """
    Plot power spectra on log-log axes.

    Gets current axis and adds plot. Can also label plot.

    Parameters
    ----------
        fs : array_like
            Frequencies
        power : array_like
            Power at given frequencies
        title : string
            Plot title
        xlabel : string
            x-axis label
        ylabel : string
            y-axis label
        legend : string
            Legend entry
        ax : matplotlib axis instance
            Axis to plot on.
    """
    if ax is None:
        ax = plt.gca()
    ax.plot(fs, power, alpha=0.8, label=legend)

    # Figure formatting
    if title is not None:
        plt.title(title)
    if legend is not None:
        plt.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xscale('log')
    ax.set_yscale('log')
