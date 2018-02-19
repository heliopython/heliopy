
import requests  # To download file
import datetime  # To find current date/time
import pandas  # For Pandas Dataframe
import os  # For extra stuff

data_source = 'http://www.sidc.be/silso/INFO/sndtotcsv.php'  # File Link
header_ = ['Y', 'M', 'D', 'DecDate', 'Daily SS', 'Std Dev', 'No Obs', 'Def/Prov Ind']

def data():
    x = str(datetime.datetime.now())[:10]+'_Sunspot_Data'+'.csv'
    if(os.path.exists(x)):  # If already downloaded
        return pandas.read_csv(x, sep=';', names=header_)
    else:
            source_csv=requests.get(data_source)  # Downloading
    if(source_csv.status_code != 200):  # File not found
        raise ValueError('URL is not a valid data source %s' %(data_source))
    else:
        with open(x, 'wb') as f:  # Write content into csv
            f.write(source_csv.content)
            return pandas.read_csv(x,sep=';',names=header_)
