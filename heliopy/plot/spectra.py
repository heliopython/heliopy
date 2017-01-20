"""Methods for plotting different types of spectra."""
import matplotlib.pyplot as plt


def loglog(fs, power, title=None, xlabel=None, ylabel=None, legend=None,
           ax=None):
    """
    Plot power spectra on log-log axes.

    Plotting is done on the current axis if present, otherwise a new axis will
    be created. Alternatively `ax` can be used to specify the axis.

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

    Examples
    --------
    A simple log-log plot:

    .. literalinclude:: /scripts/plot_loglog.py
    .. image:: /figures/plot_loglog.png
    """
    if ax is None:
        ax = plt.gca()
    ax.plot(fs, power, alpha=0.8, label=legend)

    # Figure formatting
    if title is not None:
        ax.title(title)
    if legend is not None:
        ax.legend()
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    ax.set_xscale('log')
    ax.set_yscale('log')
