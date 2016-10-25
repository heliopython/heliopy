import matplotlib.pyplot as plt


# Plots power spectral density on a log log scale
# data[:, 0] should be frequencies
# data[:, 1:] should be power
def plotloglog(data, title='', xlabel=r'$f /Hz$', ylabel='', legend=None):
    l = plt.plot(data[:, 0], data[:, 1:], alpha=0.8, label=legend)

    # Figure formatting
    plt.title(title)
    if legend is not None:
        plt.legend()
    if data.shape[1] == 4:
        plt.legend(l, (r'$x$', r'$y$', r'$z$'))
    plt.gca().set_xlabel(xlabel)
    plt.gca().set_ylabel(ylabel)
    plt.gca().set_xscale('log')
    plt.gca().set_yscale('log')
