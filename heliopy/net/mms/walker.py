import astropy.units as u
from sunpy.net.attr import AttrAnd, AttrOr, AttrWalker, SimpleAttr
from sunpy.net.attrs import Source, Time, Instrument, Level, Provider

from heliopy.net.attrs import Probe, DataRate, Version

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
def _(wlk, time_attr, param_dict):
    param_dict['start_date'] = time_attr.start.strftime('%Y-%m-%d')
    param_dict['end_date'] = (time_attr.end + 1 * u.day).strftime('%Y-%m-%d')


@walker.add_applier(Probe)
def _(wlk, attr, param_dict):
    probe_num = int(attr.value)
    param_dict['sc_id'] = f'mms{probe_num}'


@walker.add_applier(Instrument)
def _(wlk, attr, param_dict):
    param_dict['instrument_id'] = attr.value


@walker.add_applier(DataRate)
def _(wlk, attr, param_dict):
    param_dict['data_rate_mode'] = attr.value


@walker.add_applier(Level)
def _(wlk, attr, param_dict):
    param_dict['data_level'] = attr.value


@walker.add_applier(Source)
def _(wlk, attr, param_dict):
    if attr.value.lower() != 'mms':
        raise ValueError("Source isn't MMS.")


@walker.add_applier(Version)
def _(wlk, attr, param_dict):
    param_dict['version'] = attr.value
