#Obtain the data from http://www.sidc.be/silso/datafiles
#Use CSV Format
#Assuming the only data required by the user is the "Daily total sunspot number"

import requests #To download the CSV File
import datetime #To get the current date time
import pandas #To mess around with the CSV File 
import os #Operating System re

data_source = 'http://www.sidc.be/silso/INFO/sndtotcsv.php' #Link for the data source

def data(): #If the user sends a 'get' string, the module executes
    x = str(str(datetime.datetime.now())[:10]) +'_Sunspot_Data'+'.csv'    
    if(os.path.exists(x) == True):
        return pandas.read_csv(x, sep = ';', names = ['YY', 'MM', 'DD', 'DecDate', 'Daily SS.No.', 'Std. Dev.', 'No. Obs.', 'Def/Prov Ind.' ]) #Returning Pandas Dataframe
    else:
            source_csv = requests.get(data_source) #The file is downloaded into source_csv
    if(source_csv.status_code != 200): #If the file has not been successfully downloaded
        raise ValueError('URL is not a valid data source %s' %(data_source)) 
    else:
        with open(x, 'wb') as f: #Creating a .CSV file and exporting the data
            f.write(source_csv.content)
            return pandas.read_csv(x, sep = ';', names = ['YY', 'MM', 'DD', 'DecDate', 'Daily SS.No.', 'Std. Dev.', 'No. Obs.', 'Def/Prov Ind.' ]) #Returning Pandas Dataframe
         