from sunpy.net.attr import AttrAnd, AttrOr, AttrWalker, SimpleAttr
from sunpy.net.attrs import Time


__all__ = ['Dataset']


class Dataset(SimpleAttr):
    """
    The CDAWeb dataset to download.

    To find valid CDAWeb datasets, use the search functionality on this page:
    https://cdaweb.gsfc.nasa.gov/index.html . After searching for a specific
    instrument, the dataset IDs will be in bold.
    """


walker = AttrWalker()


@walker.add_creator(AttrOr)
def create_or(wlk, tree):
    results = []
    for sub in tree.attrs:
        results.append(wlk.create(sub))
    return results


@walker.add_creator(AttrAnd)
def create_and(wlk, tree):
    param_dict = {}
    wlk.apply(tree, param_dict)
    return [param_dict]


@walker.add_applier(AttrAnd)
def apply_and(wlk, and_attr, param_dict):
    for iattr in and_attr.attrs:
        wlk.apply(iattr, param_dict)


@walker.add_applier(Time)
def apply_timerange(wlk, time_attr, param_dict):
    param_dict['begin_time'] = time_attr.start
    param_dict['end_time'] = time_attr.end


@walker.add_applier(Dataset)
def _(wlk, attr, param_dict):
    param_dict['dataset'] = attr.value
