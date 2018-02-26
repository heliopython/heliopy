"""
Sunspot
-------

Methods for automatically downloading sunspot number data.

For more info about the sunspot number data, visit
http://www.sidc.be/silso/infosndtot.
"""

import requests
import datetime
import pandas
import os


class _SunspotDownloader:
    date_string = datetime.datetime.now().strftime('%Y-%m-%d')

    def __init__(self, data_source, name, header):
        self.data_source = data_source
        self.name = name
        self.header = header
        self.fname = self.date_string + '_sunspot_data_' + self.name + '.csv'

    def download(self):
        if(os.path.exists(self.fname)):  # If already downloaded
            return pandas.read_csv(self.fname, sep=';', names=self.header)
        else:
                source_csv = requests.get(self.data_source)  # Downloading
        if(source_csv.status_code != 200):  # File not found
            raise ValueError('Could not find source %s' % (self.data_source))
        else:
            with open(self.fname, 'wb') as f:  # Write content into csv
                f.write(source_csv.content)
                return pandas.read_csv(self.fname, sep=';', names=self.header)


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
