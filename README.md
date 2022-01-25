![HelioPy](https://github.com/heliopython/heliopy/raw/main/artwork/logo_rectangle.png "HelioPy")

# HelioPy is no longer developed
As of January 2022 HelioPy will no longer be developed or supported. Most of
HelioPy's functionality is now implemented elsewhere:

## Finding/loading in-situ data
[sunpy](https://docs.sunpy.org/en/stable/) version 3.1 (released October 2021)
has support for reading CDF files. It also has functionality to search NASA's
CDAWeb via. ``sunpy.net.Fido``, which provides access to in-situ data from a
large range of in-situ heliospheric observatories.

## Generating spacecraft trajectories from SPICE kernels
The [astrospice project](https://astrospice.readthedocs.io/en/latest/)
re-implements all of this functionality, in a much more user and maintainer
friendly codebase. It's currently actively developed, and accepting bug reports
or feature requests.
