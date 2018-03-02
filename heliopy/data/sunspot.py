"""
Sunspot
-------

Methods for automatically downloading sunspot number data.

For more info about the sunspot number data, visit
http://www.sidc.be/silso/datafiles.
"""

import requests
import datetime
import pandas
import os

from heliopy import config
data_dir = config['download_dir']
download_dir = os.path.join(data_dir, 'sunspot')


class _SunspotDownloader:
    date_string = datetime.datetime.now().strftime('%Y-%m-%d')

    def __init__(self, data_source, name, header):
        self.data_source = data_source
        self.name = name
        self.header = header
        self.fname = self.date_string + '_sunspot_data_' + self.name + '.csv'
        self.download_location = os.path.join(data_dir, 'sunspot', self.fname)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

    def download(self):
        # If not already downloaded
        if not os.path.exists(self.download_location):
            source_csv = requests.get(self.data_source)  # Downloading
            if(source_csv.status_code != 200):  # File not found
                raise ValueError('Could not find source %s' %
                                 (self.data_source))
            # Write content into csv
            with open(self.download_location, 'wb') as f:
                f.write(source_csv.content)

        return pandas.read_csv(self.download_location,
                               sep=';', names=self.header)


def daily():
    """
    Import daily sunspot number.

    For more information, see http://www.sidc.be/silso/infosndtot.
    """
    data_source = 'http://www.sidc.be/silso/INFO/sndtotcsv.php'
    name = 'daily'
    header = ['Y', 'M', 'D', 'DecD', 'Daily',
              'Std Dev', 'No Obs', 'Def/Prov Ind']
    Downloader = _SunspotDownloader(data_source, name, header)
    return Downloader.download()


def monthly():
    """
    Import monthly sunspot number.

    For more information, see http://www.sidc.be/silso/infosnmtot.
    """
    data_source = 'http://www.sidc.be/silso/INFO/snmtotcsv.php'
    name = 'monthly'
    header = ['Y', 'M', 'DecD', 'Monthly',
              'Std Dev ', 'No Obs', 'Def/Prov Ind']
    Downloader = _SunspotDownloader(data_source, name, header)
    return Downloader.download()


def yearly():
    """
    Import yearly sunspot number.

    For more information, see http://www.sidc.be/silso/infosnytot.
    """
    data_source = 'http://www.sidc.be/silso/INFO/snytotcsv.php'
    name = 'yearly'
    header = ['Y', 'Y_Mean',
              'Std Dev', 'No Obs', 'Def/Prov Ind']
    Downloader = _SunspotDownloader(data_source, name, header)
    return Downloader.download()
