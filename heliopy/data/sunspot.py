import requests
import datetime
import pandas
import os

data_source_daily = 'http://www.sidc.be/silso/INFO/sndtotcsv.php'
data_source_monthly = 'http://www.sidc.be/silso/INFO/snmtotcsv.php'
data_source_yearly = 'http://www.sidc.be/silso/INFO/snytotcsv.php'
head_d = ['Y', 'M', 'D', 'DecD', 'Daily', 'Std Dev', 'No Obs', 'Def/Prov Ind']
head_m = ['Y', 'M', 'DecD', 'Monthly', 'Std Dev ', 'No Obs', 'Def/Prov Ind']
head_y = ['Y', 'Y_Mean', 'Std Dev', 'No Obs', 'Def/Prov Ind']
x = str(datetime.datetime.now())[:10]


def daily():
    # For more info about the Daily Sunspot Number,
    # Visit http://www.sidc.be/silso/infosndtot
    data_source = data_source_daily
    name = x + '_Sunspot_Data_Daily' + '.csv'
    if(os.path.exists(name)):  # If already downloaded
        return pandas.read_csv(name, sep=';', names=head_d)
    else:
            source_csv = requests.get(data_source)  # Downloading
    if(source_csv.status_code != 200):  # File not found
        raise ValueError('URL is not a valid data source %s' % (data_source))
    else:
        with open(name, 'wb') as f:  # Write content into csv
            f.write(source_csv.content)
            return pandas.read_csv(name, sep=';', names=head_d)


def monthly():
    # For more info about the Monthly Sunspot Number,
    # Visit http://www.sidc.be/silso/infosnmtot
    data_source = data_source_monthly
    name = x + '_Sunspot_Data_Monthly' + '.csv'
    if(os.path.exists(name)):  # If already downloaded
        return pandas.read_csv(name, sep=';', names=head_m)
    else:
            source_csv = requests.get(data_source)  # Downloading
    if(source_csv.status_code != 200):  # File not found
        raise ValueError('URL is not a valid data source %s' % (data_source))
    else:
        with open(name, 'wb') as f:  # Write content into csv
            f.write(source_csv.content)
            return pandas.read_csv(name, sep=';', names=head_m)


def yearly():
    # For more info about the Yearly Sunspot Number,
    # Visit http://www.sidc.be/silso/infosnytot
    data_source = data_source_yearly
    name = x + '_Sunspot_Data_Yearly' + '.csv'
    if(os.path.exists(name)):  # If already downloaded
        return pandas.read_csv(name, sep=';', names=head_y)
    else:
            source_csv = requests.get(data_source)  # Downloading
    if(source_csv.status_code != 200):  # File not found
        raise ValueError('URL is not a valid data source %s' % (data_source))
    else:
        with open(name, 'wb') as f:  # Write content into csv
            f.write(source_csv.content)
            return pandas.read_csv(name, sep=';', names=head_y)
