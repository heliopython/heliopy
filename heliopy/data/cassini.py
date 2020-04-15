"""
Methods for importing data from the Cassini spacecraft.
"""
import datetime
import os
import pathlib
import pandas as pd
import calendar
import astropy.units as u
import pvl
import shutil
import zipfile
from glob import glob
import numpy as np
import csv
from struct import unpack, calcsize

from collections import OrderedDict
from heliopy.data import util
from heliopy import config

data_dir = pathlib.Path(config['download_dir'])
use_hdf = config['use_hdf']
cassini_dir = data_dir / 'cassini'

# These mappings from months to strings are used in directory names
month2str = {1: '001_031_JAN',
             2: '032_059_FEB',
             3: '060_090_MAR',
             4: '091_120_APR',
             5: '121_151_MAY',
             6: '152_181_JUN',
             7: '182_212_JUL',
             8: '213_243_AUG',
             9: '244_273_SEP',
             10: '274_304_OCT',
             11: '305_334_NOV',
             12: '335_365_DEC'}
leapmonth2str = {1: '001_031_JAN',
                 2: '032_060_FEB',
                 3: '061_091_MAR',
                 4: '092_121_APR',
                 5: '122_152_MAY',
                 6: '153_182_JUN',
                 7: '183_213_JUL',
                 8: '214_244_AUG',
                 9: '245_274_SEP',
                 10: '275_305_OCT',
                 11: '306_335_NOV',
                 12: '336_366_DEC'}


class _mag1minDownloader(util.Downloader):
    def __init__(self, coords):
        valid_coords = ['KRTP', 'KSM', 'KSO', 'RTN']
        if coords not in valid_coords:
            raise ValueError('coords must be one of {}'.format(valid_coords))
        self.coords = coords

        Rs = u.def_unit('saturnRad', 60268 * u.km)
        if (coords == 'KRTP'):
            self.units = OrderedDict([('Bx', u.nT), ('By', u.nT), ('Bz', u.nT),
                                      ('X', Rs), ('|B|', u.nT),
                                      ('Y', u.deg),
                                      ('Z', u.deg),
                                      ('Local hour', u.dimensionless_unscaled),
                                      ('n points', u.dimensionless_unscaled)])
        if (coords == 'RTN'):
            self.units = OrderedDict([('Bx', u.nT), ('By', u.nT), ('Bz', u.nT),
                                      ('X', u.AU), ('Y', u.AU), ('Z', u.AU),
                                      ('|B|', u.nT),
                                      ('Local hour', u.dimensionless_unscaled),
                                      ('n points', u.dimensionless_unscaled)])
        if (coords == 'KSM' or coords == 'KSO'):
            self.units = OrderedDict([('Bx', u.nT), ('By', u.nT), ('Bz', u.nT),
                                      ('X', Rs), ('Y', Rs), ('Z', Rs),
                                      ('|B|', u.nT),
                                      ('Local hour', u.dimensionless_unscaled),
                                      ('n points', u.dimensionless_unscaled)])

    def intervals(self, starttime, endtime):
        return self.intervals_yearly(starttime, endtime)

    def fname(self, interval):
        year = interval.start.strftime('%Y')
        return f'{year}_FGM_{self.coords}_1M.TAB'

    def local_dir(self, interval):
        return pathlib.Path('cassini') / 'mag' / '1min'

    def download(self, interval):
        local_dir = self.local_path(interval).parent
        local_dir.mkdir(parents=True, exist_ok=True)
        year = interval.start.strftime('%Y')
        base_url = ('http://pds-ppi.igpp.ucla.edu/ditdos/download?'
                    'id=pds://PPI/CO-E_SW_J_S-MAG-4-SUMM-1MINAVG-V2.0/DATA')
        url = '{}/{}'.format(base_url, year)
        util._download_remote(url,
                              self.fname(interval),
                              local_dir)

    def load_local_file(self, interval):
        f = open(self.local_path(interval))
        if 'error_message' in f.readline():
            f.close()
            os.remove(f.name)
            raise util.NoDataError()
        data = pd.read_csv(f,
                           names=['Time', 'Bx', 'By', 'Bz', '|B|',
                                  'X', 'Y', 'Z', 'Local hour', 'n points'],
                           delim_whitespace=True,
                           parse_dates=[0], index_col=0)
        f.close()
        return data


def mag_1min(starttime, endtime, coords):
    """
    Import 1 minute magnetic field from Cassini.

    See http://pds-ppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/CO-E_SW_J_S-MAG-4-SUMM-1MINAVG-V1.0
    for more information.

    Cassini Orbiter Magnetometer Calibrated MAG data in 1 minute averages
    available covering the period 1999-08-16 (DOY 228) to 2016-12-31 (DOY 366).
    The data are provided in RTN coordinates throughout the mission, with
    Earth, Jupiter, and Saturn centered coordinates for the respective
    flybys of those planets.

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.
    coords : strings
        Requested coordinate system. Must be one of
        ``['KRTP', 'KSM', 'KSO', 'RTN']``

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Requested data
    """
    dl = _mag1minDownloader(coords)
    return dl.load(starttime, endtime)


def mag_hires(starttime, endtime, try_download=True):
    """
    Import high resolution magnetic field from Cassini.

    See http://pds-ppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/CO-E_SW_J_S-MAG-3-RDR-FULL-RES-V1.0
    for more information.

    Cassini Orbiter Magnetometer Calibrated MAG data at the highest time
    resolution available covering the period 1999-08-16 (DOY 228) to
    2016-12-31 (DOY 366).

    The data are in RTN coordinates prior Cassini's arrival at Saturn, and
    Kronographic (KRTP) coordinates at Saturn (beginning 2004-05-14, DOY 135).

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Requested data
    """
    remote_base_url = ('http://pds-ppi.igpp.ucla.edu/ditdos/download?id='
                       'pds://PPI/CO-E_SW_J_S-MAG-3-RDR-FULL-RES-V2.0/DATA')
    dirs = []
    fnames = []
    extension = '.TAB'
    units = OrderedDict([('Bx', u.nT), ('By', u.nT), ('Bz', u.nT),
                         ('coords', u.dimensionless_unscaled)])
    local_base_dir = cassini_dir / 'mag' / 'hires'

    for [day, _, _] in util._daysplitinterval(starttime, endtime):
        year = day.year
        if calendar.isleap(year):
            monthstr = leapmonth2str[day.month]
        else:
            monthstr = month2str[day.month]

        if day < datetime.date(2004, 5, 14):
            coords = 'RTN'
        else:
            coords = 'KRTP'
        doy = day.strftime('%j')
        dirs.append(pathlib.Path(str(year)) / monthstr)
        fnames.append(str(year)[2:] + doy + '_FGM_{}'.format(coords))

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        url = remote_base_url + '/' + str(directory)
        util._download_remote(url, fname + extension,
                              local_base_dir / directory)

    def processing_func(f):
        if 'error_message' in f.readline():
            f.close()
            os.remove(f.name)
            raise util.NoDataError()
        df = pd.read_csv(f, names=['Time', 'Bx', 'By', 'Bz'],
                         delim_whitespace=True,
                         parse_dates=[0], index_col=0)
        return df

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units,
                        try_download=try_download)


def caps_dateparser(stringlist):
    return [datetime.datetime.strptime(item,"%Y-%jT%H:%M:%S.%f") for item in stringlist]

def caps_els(starttime, endtime, try_download=True):
    """
    Import Cassini Plasma Spectrometer Electron Spectrometer.

    See https://pds-ppi.igpp.ucla.edu/search/view/?id=pds://PPI/CO-E_J_S_SW-CAPS-3-CALIBRATED-V1.0
    for more information.

    Cassini Plasma Spectrometer Electron Spectrometer data at the highest time
    resolution available covering the periods
    1999-004 (4 Jan) to 1999-021 (21 Jan), 
    1999-232 (20 Aug) to 1999-257 (14 Sep), 
    2000-190 (8 Jul) to 2000-309 (4 Nov), 
    2001-120 (30 Apr)to 2004-135 (14 May), 
    at Earth from 1999-229 (17 Aug) to 1999-231 (19 Aug), 
    at Jupiter from 2000-310 (4 Nov) to 2001-119 (29 Apr), 
    at Saturn over the interval 2004-136 (15 May) to 2012-154 (02 Jun).

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Requested data
    """
    remote_base_url = ('https://pds-ppi.igpp.ucla.edu/ditdos/download?id='
                       'pds://PPI/CO-E_J_S_SW-CAPS-3-CALIBRATED-V1.0/DATA/CALIBRATED')
    dirs = []
    fnames = []
    extension = ''
    units = OrderedDict([])
    local_base_dir = cassini_dir / 'caps' / 'els'

    for [day, _, _] in util._daysplitinterval(starttime, endtime):
        year = day.year
        if calendar.isleap(year):
            monthstr = leapmonth2str[day.month]
        else:
            monthstr = month2str[day.month]
            
        doy = day.strftime('%j')
        for x in ['00','06','12','18']:
            dirs.append(pathlib.Path(str(year)) / doy)
            fnames.append('ELS_' + str(year) + doy + x + '_V01')    
    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        url = remote_base_url + '/' + str(directory)
        util._download_remote(url, fname + extension,
                              local_base_dir / directory)

    def processing_func(f):
        oldfilename_path = pathlib.Path(str(f.name))
        zip_path = pathlib.Path(str(f.name)+".zip")     
        f.close()
        shutil.copy(oldfilename_path.__str__(),zip_path.__str__())
        
        extractdir_path = oldfilename_path.parents[0] / "temp"
        zipfile.ZipFile(zip_path.__str__()).extractall(extractdir_path.__str__())
        formatfilepath = sorted(extractdir_path.rglob("*.FMT"))[0]
        labelfilepath = sorted(extractdir_path.rglob("*.LBL"))[0]
        datafilepath = sorted(extractdir_path.rglob("*.DAT"))[0]

        datatype_dict = {"DATE":"21s",'LSB_UNSIGNED_INTEGER':'B','LSB_UNSIGNED_INTEGER':'I','PC_REAL':'f'}


        fmt_i = '<' #start little endian
        fmt_o = ''
        column_headers=[]
        columncounter = 0
        for item in pvl.load(formatfilepath.__str__()).items():
            if item[1]['NAME'] == 'DEAD_TIME_METHOD' and item[1]['BYTES'] == 1 and item[1]['DATA_TYPE'] == 'LSB_UNSIGNED_INTEGER':
                fmt_i += 'B'
                fmt_o += '%u\t'
                column_headers.append(item[1]['NAME'])
                continue
            elif item[1]['NAME'] == 'TELEMETRY' and item[1]['BYTES'] == 2 and item[1]['DATA_TYPE'] == 'LSB_UNSIGNED_INTEGER':
                fmt_i += 'H'
                fmt_o += '%u\t'
                column_headers.append(item[1]['NAME'])
                continue
            elif 'ITEMS' in item[1].keys():
                fmt_i += datatype_dict[item[1]['DATA_TYPE']]*item[1]['ITEMS']   
                fmt_o += '%f\t'*item[1]['ITEMS']

                column_countertemp = [item[1]['NAME']+'_'+str(x) for x in np.arange(1,item[1]['ITEMS']+1,1)]
                column_headers += column_countertemp
                continue
            else:        
                fmt_i += datatype_dict[item[1]['DATA_TYPE']]
                
                if datatype_dict[item[1]['DATA_TYPE']] == 'f':
                    fmt_o += '%f\t'
                    column_headers.append(item[1]['NAME'])
                elif item[1]['DATA_TYPE'] == 'DATE':  
                    fmt_o += '%s\t'
                    column_headers.append("Time")
                continue

        fmt_o += '\n'
        fmtsz = calcsize(fmt_i)

        #Checks the size dervied from format file against the label file
        if fmtsz != pvl.load(labelfilepath.__str__())['TABLE']['ROW_BYTES']:
            raise ValueError("Format file disagrees with label file")
        
        temptextfile_path = pathlib.Path(str(f.name) + '.txt')
        #Read the Binary data into a temp .txt file
        datainputfile = open(datafilepath.__str__(),'rb')
        textoutputfile = open(temptextfile_path.__str__(),'w')
        while True:
            entry = datainputfile.read(fmtsz) # read file
            if not entry:
                break # EOF yields null string, exit loop
            data = unpack(fmt_i,entry) # unpack the record using the defined input format
            textoutputfile.write(fmt_o%data) # write to output file using the defined output format
        datainputfile.close() # close input file
        textoutputfile.close() # close output file

        
        #Writes to a .csv
        csvoutputfile = oldfilename_path.__str__()+'.csv'
        filein = open(temptextfile_path.__str__(), "r")
        in_txt = csv.reader(filein, delimiter = '\t')
        
        with open(csvoutputfile , 'w',newline='') as fileout:
            out_csv = csv.writer(fileout, delimiter = '\t')
            out_csv.writerow(column_headers) 
            for line in in_txt:
                newline = [line[0][2:-1]] + line[1:]
                out_csv.writerow(newline)        
        filein.close()
        
        
        #Tidying up        
        temptextfile_path.unlink()
        #oldfilename_path.unlink()
        zip_path.unlink()
        shutil.rmtree(extractdir_path)
        
        df = pd.read_csv(csvoutputfile, header=0,
                         delim_whitespace=True,
                         parse_dates=[0], index_col=0,
                         date_parser=caps_dateparser)        
        return df

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units,
                        try_download=try_download)