import matplotlib.pyplot as plt


def loglog(fs, power, title='', xlabel=r'$f /Hz$', ylabel='', legend=None):
    '''
    A method to plot power spectra on log-log axes
    '''
    ax = plt.gca()
    l = ax.plot(fs, power, alpha=0.8, label=legend)

    # Figure formatting
    plt.title(title)
    if legend is not None:
        plt.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xscale('log')
    ax.set_yscale('log')
