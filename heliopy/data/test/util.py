import astropy.units as u
import pandas as pd
import sunpy


def check_data_output(df):
    '''
    Function to check that the output of a data fetch method.
    '''
    check_units(df)
    if type(df) is sunpy.timeseries.timeseriesbase.GenericTimeSeries:
        df = df.data
    check_datetime_index(df)
    assert df.shape[0] > 0
    assert df.shape[1] > 0


def check_datetime_index(df):
    'Helper funciton to check all dataframes have a datetime index'
    assert type(df.index[0]) == pd.Timestamp


def check_units(df):
    if type(df) is not sunpy.timeseries.timeseriesbase.GenericTimeSeries:
        warnings.warn("Function has no units attached", RuntimeWarning)
        assert type(df.index[0]) == pd.Timestamp
    else:
        for column in df.data.columns:
            assert type(df.quantity(column)) == u.quantity.Quantity
