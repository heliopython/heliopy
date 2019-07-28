"""
Methods for importing data from the four MMS spacecraft.

All data is publically available at
https://lasp.colorado.edu/mms/sdc/public/data/, and the MMS science data centre
is at https://lasp.colorado.edu/mms/sdc/public/.
"""
import pdb

import os
import datetime as dt
import pathlib
from collections import OrderedDict
import requests
from tqdm.auto import tqdm

from heliopy.data import util
from heliopy import config

import sunpy
import glob
import glob, os, requests
# from tqdm import tqdm
from urllib.parse import parse_qs


data_dir = pathlib.Path(config['download_dir'])
mms_dir = data_dir / 'mms'
mms_url = 'https://lasp.colorado.edu/mms/sdc/public'
remote_mms_dir = mms_url + '/data/'
query_url = mms_url + '/files/api/v1/file_names/science'
dl_url = mms_url + '/files/api/v1/download/science'


class MMSDownloader(util.Downloader):
    """
    Download data from the Magnetospheric Multiscale (MMS) Science
    Data Center (SDC). Data can be found at
    
    https://lasp.colorado.edu/mms/sdc/

    The following methods must be implemented by sub-classes:

    - :meth:`Downloader.intervals()`: given a time interval, this
      method should split the interval up into sub-intervals. Each of these
      sub-intervals corresponds directly to a single file to download, store,
      and read in.
    - :meth:`Downloader.local_dir()`: given an interval, returns the
      local directory in which the file is stored.
    - :meth:`Downloader.fname()`: given an interval, returns the
      local filename in which the file is stored.
    - :meth:`Downloader.download()`: given an interval, download the data for
      that interval.
    - :meth:`Downloader.load_local_file()`: given an interval, load the local
      file and return a :class:`pandas.DataFrame` object containing the data.
    """
    def __init__(self, sc=None, instr=None, mode=None, level=None,
                 anc_product=None,
                 data_type='science',
                 data_root=None,
                 dropbox_root=None,
                 end_date=None,
                 files=None,
                 mirror_root=None,
                 offline=False,
                 optdesc=None,
                 site='public',
                 start_date=None,
                 version=None):
        
        # Set attributes
        #   - Put site before level because level will auto-set site
        #   - Put files last because it will reset most fields
        self.site = site
        
        self.anc_product = anc_product
        self.data_type = data_type
        self.dropbox_root = dropbox_root
        self.end_date = end_date
        self.instr = instr
        self.level = level
        self.mirror_root = mirror_root
        self.mode = mode
        self.offline = offline
        self.optdesc = optdesc
        self.sc = sc
        self.start_date = start_date
        self.version = version
        
        self.files = files
        
        # Setup download directory
        #   - $HOME/data/mms/
        if data_root is None:
            data_root = os.path.join(os.path.expanduser('~'), 'data', 'mms')
            if not os.path.isdir(data_root):
                os.makedirs(data_root, exist_ok=True)
        
        self.data_root  = data_root
        self._sdc_home  = 'https://lasp.colorado.edu/mms/sdc'
        self._info_type = 'download'
        
        # Create a persistent session
        self._session = requests.Session()
    
    def __str__(self):
        return self.url()
    
    # https://stackoverflow.com/questions/17576009/python-class-property-use-setter-but-evade-getter
    def __setattr__(self, name, value):
        """Control attribute values as they are set."""
        
        # TYPE OF INFO
        #   - Unset other complementary options
        #   - Ensure that at least one of (download | file_names | 
        #     version_info | file_info) are true
        if name == 'anc_product':
            self.data_type = 'ancillary'
        elif name == 'data_type':
            if value not in ('ancillary', 'hk', 'science'):
                raise ValueError('Invalid value for attribute "' + name + '".')
        elif name == 'files':
            if value is not None:
                self.sc = None
                self.instr = None
                self.mode = None
                self.level = None
                self.optdesc = None
                self.version = None
        elif name == 'level':
            if value in [None, 'l2', 'l3']:
                self.site = 'public'
            else:
                self.site = 'private'
        
        # Set the value
        super(MMSDownloader, self).__setattr__(name, value)
    
    
    def intervals(self, starttime=None, endtime=None):
        """
        The complete list of sub-intervals that cover a time range
        Each sub-interval is associated with a single file to be downloaded and
        read in.
        
        Parameters
        ----------
        starttime : datetime.datetime
            Start time of interval within which data sub-intervals are determined.
        endtime : datetime.datetime
            End time of interval within which data sub-intervals are determined.

        Returns
        -------
        fnames : list of sunpy.time.TimeRange
            List of intervals
        """
        
        if starttime:
            self.start_date = starttime
        if endtime:
            self.end_date = endtime
        
        # Start time from file names
        fnames = self.file_names()
        nfiles = len(fnames)
        parts = parse_file_name(fnames)
        
        # MMS files do not have end times in their file names and burst files
        # do not have a fixed start time or duration (although survey files do).
        # Assume the end time of one file is a microsecond before the start time
        # of the next file in sequence (or the end of the time interval, if
        # sooner). Step through files backwards, since end[i-1] depends on start[i].
        trange = [sunpy.time.TimeRange()]*nfiles
        for i in range(nfiles-1, 0, -1):
            # Start tiem of interval
            if len(parts[i][5]) == 8:
                trange[i].start = dt.datetime.strptime(p[5], '%Y%m%d')
            else:
                trange[i].start = dt.datetime.strptime(p[5], '%Y%m%d%H%M%S')
            
            # End time of interval
            if i == (nfiles-1):
                trange[i].end = self._end_date
            elif i > 0:
                trange[i-1].end = trange[i].start - dt.timedelta(seconds=1e-6)
        
        return trange
    
    
    def local_dir(self, interval=None):
        """
        Local directory for a given interval.

        Parameters
        ----------
        interval : sunpy.time.TimeRange

        Returns
        -------
        dir : pathlib.Path
            Local directory
        """
        if interval:
            self.start_date = interval.start
            self.end_date = interval.end
        
        # Create a list of sequential dates spanning the time interval
        ndays = (self._end_date - self._start_date).days
        dates = ['']*(ndays+1)
        for i in range(ndays+1):
            date = self._start_date + dt.timedelta(days=i)
            dates[i] = date.strftime('%Y%m%d')
        
        # Create the local directories
        dirs = construct_path(self.sc, self.instr, self.mode, self.level, dates,
                              optdesc=self.optdesc, root=self.data_root)
        return dirs
    
    
    def fname(self, interval=None, mirror=False):
        """
        Return the filename for a given interval.

        Parameters
        ----------
        interval : sunpy.time.TimeRange

        Returns
        -------
        fname : str or list
            Filename
        """
        if interval:
            self.start_date = interval.start
            self.end_date = interval.end
        
        # Search the mirror or local directory
        if mirror:
            data_root = self.mirror_root
        else:
            data_root = self.data_root
        
        # If no start or end date have been defined,
        #   - Start at beginning of mission
        #   - End at today's date
        start_date = self._start_date
        end_date = self._end_date
        if self._start_date is None:
            start_date = dt.datetime(2015, 9, 1)
        if self._end_date is None:
            end_date = dt.datetime.today()
        
        # Create all dates between start_date and end_date
        deltat = dt.timedelta(days=1)
        dates  = []
        while start_date <= end_date:
            dates.append(start_date.strftime('%Y%m%d'))
            start_date += deltat
        
        # Paths in which to look for files
        #   - Files of all versions and times within interval
        paths = construct_path(self.sc, self.instr, self.mode, self.level,
                               dates, optdesc=self.optdesc,
                               root=data_root, files=True)
        
        # Search
        result = []
        pwd = os.getcwd()
        for path in paths:
            root = os.path.dirname(path)
            
            try:
                os.chdir(root)
            except FileNotFoundError:
                continue
            except:
                os.chdir(pwd)
                raise
                
            for file in glob.glob(os.path.basename(path)):
                result.append(os.path.join(root, file))

        os.chdir(pwd)
        
        return result
    
    
    def url(self):
        """Build a URL to query the SDC."""
        sep = '/'
        url = sep.join( (self._sdc_home, self.site, 'files', 'api', 'v1', 
                         self._info_type, self.data_type) )
        
        # Build query from parts of file names
        query = '?'
        qdict = self.query()
        for key in qdict:
            query += key + '=' + qdict[key] + '&'
        
        # Combine URL with query string
        url += query
        return url
    
    
    def check_response(self, response):
        '''Check the status code for a requests response and perform
           and appropriate action (e.g. log-in, raise error, etc.)
        
        Parameters:
        -----------
        response (object):      A requests response object
        '''
        
        # OK
        if response.status_code == 200:
            r = response
        
        # Authentication required
        elif response.status_code == 401:
            print('Log-in Required')
            
            maxAttempts = 3
            nAttempts = 1
            while nAttempts <= maxAttempts:
                # Save log-in credentials and request again
                self.login()
                
                # Remake the request
                #   - Ideally, self._session.send(response.request)
                #   - However, the prepared request lacks the authentication data
                if response.request.method == 'POST':
                    query = parse_qs(response.request.body)
                    r = self._session.post(response.request.url, data=query)
                else:
                    r = self._session.get(response.request.url)
                
                # Another attempt
                if r.ok:
                    break
                else:
                    Print('Incorrect username or password. %d tries remaining.' % maxAttempts-nAttemps)
                    nAttempts += 1
            
            # Failed log-in
            if nAttempts > maxAttempts:
                raise ConnectionError('Failed log-in.')
        
        else:
            raise ConnectionError(r.reason)
        
        # Return the resulting request
        return r
    
    
    def download(self):
        self._info_type = 'download'
        # Build the URL sans query
        url = '/'.join((self._sdc_home, self.site, 'files', 'api', 'v1',
                        self._info_type, self.data_type))
        
        # Get available files
        local_files, remote_files = self.search()
        if self.offline:
            return local_files
        
        # Get information on the files that were found
        #   - To do that, specify the specific files. This sets all other properties to None
        #   - Save the state of the object as it currently is so that it can be restored
        #   - Setting FILES will indirectly cause SITE='public'. Keep track of SITE.
        site = self.site
        state = {}
        state['sc'] = self.sc
        state['instr'] = self.instr
        state['mode'] = self.mode
        state['level'] = self.level
        state['optdesc'] = self.optdesc
        state['version'] = self.version
        state['files'] = self.files
        self.files = [file.split('/')[-1] for file in remote_files]
        
        self.site = site
        file_info = self.file_info()
        
        # Amount to download per iteration
        block_size = 1024*128
        
        # Download each file individually
        for info in file_info['files']:
            # Create the destination directory
            file = self.name2path(info['file_name'])
            if not os.path.isdir(os.path.dirname(file)):
                os.makedirs(os.path.dirname(file))
            
            # downloading: https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
            # progress bar: https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
            try:
                r = self._session.post(url,
                                       data={'file': info['file_name']}, 
                                       stream=True)
                with tqdm(total=info['file_size'], unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                    with open(file, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=block_size):
                            if chunk: # filter out keep-alive new chunks
                                f.write(chunk)
                                pbar.update(block_size)
            except:
                if os.path.isfile(file):
                    os.remove(file)
                for key in state:
                    self.files = None
                    setattr(self, key, state[key])
                raise
            
            local_files.append(file)
        
        for key in state:
            self.files = None
            setattr(self, key, state[key])
        
        return local_files
    
    
    def load_local_file(self, starttime=None, endtime=None):
        if starttime:
            self.start_date = starttime
        if endtime:
            self.end_date = endtime
        
        # Download the files
        #   - If already downloaded, returns local files
        files = self.download()
        
    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
            url = remote_base_url + '?file=' + fname + extension
            local_fname = os.path.join(local_base_dir, fname + extension)
            with requests.get(url, stream=True) as request:
                with open(local_fname, 'wb') as fd:
                    for chunk in tqdm(
                            request.iter_content(chunk_size=128)):
                        fd.write(chunk)

    def processing_func(cdf):
        return util.cdf2df(cdf, index_key='Epoch')

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime,
                        warn_missing_units=warn_missing_units)
    
    
    def file_info(self):
        """Obtain file information from the SDC."""
        self._info_type = 'file_info'
        response = self.get()
        return response.json()
        
    
    def file_names(self):
        """Obtain file names from the SDC."""
        self._info_type = 'file_names'
        response = self.get()
        
        if response.text == '':
            files = []
        else:
            files = filter_time(response.text.split(','),
                                self.start_date, self.end_date)
        
        return files
    
    
    def local_file_names(self, mirror=False):
        """Search for MMS files on the local system.
        
        Files must be located in an MMS-like directory structure.
        
        ***REPLACED BY FNAME***
        """
        
        # Search the mirror or local directory
        if mirror:
            data_root = self.mirror_root
        else:
            data_root = self.data_root
        
        # If no start or end date have been defined,
        #   - Start at beginning of mission
        #   - End at today's date
        start_date = self._start_date
        end_date = self._end_date
        if self._start_date is None:
            start_date = dt.datetime(2015, 9, 1)
        if self._end_date is None:
            end_date = dt.datetime.today()
        
        # Create all dates between start_date and end_date
        deltat = dt.timedelta(days=1)
        dates  = []
        while start_date <= end_date:
            dates.append(start_date.strftime('%Y%m%d'))
            start_date += deltat
        
        # Paths in which to look for files
        #   - Files of all versions and times within interval
        paths = construct_path(self.sc, self.instr, self.mode, self.level,
                               dates, optdesc=self.optdesc,
                               root=data_root, files=True)
        
        # Search
        result = []
        pwd = os.getcwd()
        for path in paths:
            root = os.path.dirname(path)
            
            try:
                os.chdir(root)
            except FileNotFoundError:
                continue
            except:
                os.chdir(pwd)
                raise
                
            for file in glob.glob(os.path.basename(path)):
                result.append(os.path.join(root, file))

        os.chdir(pwd)
        
        return result
    
    
    def login(self, username=None, password=None):
        """Log-In to the SDC
        
        Parameters
        ----------
        username (str):     Account username
        password (str):     Account password
        """
        
        # Ask for inputs
        if username is None:
            username = input('username: ')
        if password is None:
            password = input('password: ')
        
        # Save credentials
        self._session.auth = (username, password)
    
    
    def get(self):
        """Retrieve data from the SDC.
        """
        # Build the URL sans query
        url = '/'.join((self._sdc_home, self.site, 'files', 'api', 'v1',
                        self._info_type, self.data_type))
        
        # Check on query
        r = self._session.post(url, data=self.query())
        
        # Check if everything is ok
        if not r.ok:
            r = self.check_response(r)
        
        # Return the response for the requested URL
        return r
    
    
    def name2path(self, filename):
        """Convert remote file names to local file name.
        
        Directories of a remote file name are separated by the '/' character,
        as in a web address.
        
        Parameters
        ----------
        filename:  str
                   File name for which the local path is desired.
        
        Returns
        -------
        local_name:  Equivalent local file name. This is the location to
                     which local files are downloaded.
        """
        parts = filename.split('_')
        
        # Burst directories and file names are structured as:
        #   - dirname:  sc/instr/mode/level[/optdesc]/YYYY/MM/DD/
        #   - basename: sc_instr_mode_level[_optdesc]_YYYYMMDDhhmmss_vX.Y.Z.cdf
        # Index from end to catch the optional descriptor, if it exists
        if parts[2] == 'brst':
            path = os.path.join(self.data_root, *parts[0:-2],
                                parts[-2][0:4], parts[-2][4:6],
                                parts[-2][6:8], filename)
        
        # Survey (slow,fast,srvy) directories and file names are structured as:
        #   - dirname:  sc/instr/mode/level[/optdesc]/YYYY/MM/
        #   - basename: sc_instr_mode_level[_optdesc]_YYYYMMDD_vX.Y.Z.cdf
        # Index from end to catch the optional descriptor, if it exists
        else:
            path = os.path.join(self.data_root, *parts[0:-2],
                                parts[-2][0:4], parts[-2][4:6], filename)
        
        return path
    
    def parse_file_name(self, filename):
        """Parse file names.
        
        Parse official MMS file names. MMS file names are formatted as
            sc_instr_mode_level[_optdesc]_tstart_vX.Y.Z.cdf
        where
            sc:       spacecraft id
            instr:    instrument id
            mode:     data rate mode
            level:    data level
            optdesc:  optional filename descriptor
            tstart:   start time of file
            vX.Y.Z    file version, with X, Y, and Z version numbers
        
        Params:
        filename (str):  An MMS file name
        
        Returns:
        parts (tuple):  A tuples ordered as
                        (sc, instr, mode, level, optdesc, tstart, version)
                        If opdesc is not present in the file name, the output will
                        contain the empty string ('').
        """
        parts = os.path.basename(filename).split('_')
        
        # If the file does not have an optional descriptor, 
        # put an empty string in its place.
        if len(parts) == 6:
            parts.insert(-2, '')
            
        # Remove the file extension ``.cdf''
        parts[-1] = parts[-1][0:-4]
        return tuple(parts)
    
    
    def query(self):
        
        # Adjust end date
        #   - The query takes '%Y-%m-%d' but the object allows '%Y-%m-%dT%H:%M:%S'
        #   - Further, the query is half-exclusive: [start, end)
        #   - If the dates are the same but the times are different, then files between
        #     self.start_date and self.end_date will not be found
        #   - In these circumstances, increase the end date by one day
        end_date = self._end_date
        if end_date is not None:
            end_date = self._end_date.strftime('%Y-%m-%d')
            if self._start_date.date() == self._end_date.date() or self._end_date.time() != dt.time(0,0,0):
                end_date = (self._end_date + dt.timedelta(1)).strftime('%Y-%m-%d')
        
        query = {}
        if self.sc is not None:
            query['sc_id'] = self.sc if isinstance(self.sc, str) else ','.join(self.sc)
        if self.instr is not None:
            query['instrument_id'] = self.instr if isinstance(self.instr, str) else ','.join(self.instr)
        if self.mode is not None:
            query['data_rate_mode'] = self.mode if isinstance(self.mode, str) else ','.join(self.mode)
        if self.level is not None:
            query['data_level'] = self.level if isinstance(self.level, str) else ','.join(self.level)
        if self.optdesc is not None:
            query['descriptor'] = self.optdesc if isinstance(self.optdesc, str) else ','.join(self.optdesc)
        if self.version is not None:
            query['version'] = self.version if isinstance(self.version, str) else ','.join(self.version)
        if self.files is not None:
            query['files'] = self.files if isinstance(self.files, str) else ','.join(self.files)
        if self.start_date is not None:
            query['start_date'] = self._start_date.strftime('%Y-%m-%d')
        if self.end_date is not None:
            query['end_date'] = end_date
        
        return query
    
    
    def remote2localnames(self, remote_names):
        """Convert remote file names to local file names.
        
        Directories of a remote file name are separated by the '/' character,
        as in a web address.
        
        Parameters:
        remote_names (list): Remote file names returned by FileNames.
        
        Returns:
        local_names (list):  Equivalent local file name. This is the location to
                             which local files are downloaded.
        """
        # os.path.join() requires string arguments, but str.split() return list.
        #   - Unpack with *: https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
        local_names =list()
        for file in remote_names:
            local_names.append(os.path.join(self.data_root, *file.split('/')[2:]))
        
        if (len(remote_names) == 1) & (type(remote_names) == 'str'):
            local_names = local_names[0]
        
        return local_names
    
    
    def search(self):
        """Search for files locally and at the SDC.
        
        TODO:
            Filter results in self.Local_FileNames() by time and remove the time
            filters here. self.FileNames() already filters by time.
        
        Returns:
        files (tuple):  Local and remote files within the interval, returned as
                        (local, remote), where `local` and `remote` are lists.
        """
        
        # Search locally if offline
        if self.offline:
            local_files = self.local_file_names()
            remote_files = []
        
        # Search remote first
        #   - SDC is definitive source of files
        #   - Returns most recent version
        else:
            remote_files = self.file_names()
            
            # Search for the equivalent local file names
            local_files = self.remote2localnames(remote_files)
            idx = [i for i, local in enumerate(local_files) if os.path.isfile(local)]
            
            # Filter based on location
            local_files = [local_files[i] for i in idx]
            remote_files = [remote_files[i] for i in range(len(remote_files)) if i not in idx]
        
        # Filter based on time interval
        if len(local_files) > 0:
            local_files = filter_time(local_files, self.start_date, self.end_date)
        if len(remote_files) > 0:
            remote_files = filter_time(remote_files, self.start_date, self.end_date)
        
        return (local_files, remote_files)
    
    
    def version_info(self):
        """Obtain version information from the SDC."""
        self._info_type = 'version_info'
        response = self.Get()
        return response.json()
    
    
    @property
    def site(self):
        return self._site
    
    @site.setter
    def site(self, value):
        if (value == 'team') | (value == 'team_site') | (value == 'sitl') | (value == 'private'):
            self._site = 'sitl'
        elif (value == 'public') | (value == 'public_site'):
            self._site = 'public'
        else:
            raise ValueError('Invalid value for the "site" attribute')
    
    @property
    def start_date(self):
        if isinstance(self._start_date, dt.datetime):
            theDate = self._start_date.isoformat()
        else:
            theDate = self._start_date
        
        return theDate
    
    @start_date.setter
    def start_date(self, value):
        # Convert string to datetime object
        if isinstance(value, str):
            try:
                value = dt.datetime.strptime(value[0:19], '%Y-%m-%dT%H:%M:%S')
            except:
                try:
                    value = dt.datetime.strptime(value, '%Y-%m-%d')
                except:
                    ValueError('Invalid format for attribute start_date.')
        
        self._start_date = value
    
    
    @property
    def end_date(self):
        if isinstance(self._end_date, dt.datetime):
            theDate = self._end_date.isoformat()
        else:
            theDate = self._end_date
        
        return theDate
    
    
    @end_date.setter
    def end_date(self, value):
        # Convert string to datetime object
        if isinstance(value, str):
            try:
                value = dt.datetime.strptime(value[0:19], '%Y-%m-%dT%H:%M:%S')
            except:
                try:
                    value = dt.datetime.strptime(value, '%Y-%m-%d')
                except:
                    ValueError('Invalid format for attribute start_date.')
        
        self._end_date = value




def construct_filename(sc, instr=None, mode=None, level=None, tstart='*', version='*',
                       optdesc=None):
    """
    Construct a file name compliant with MMS file name format guidelines.
    
    MMS file names follow the convention
        sc_instr_mode_level[_optdesc]_tstart_vX.Y.Z.cdf
    
    Arguments:
        sc (str,list,tuple):   Spacecraft ID(s)
        instr   (str,list):    Instrument ID(s)
        mode    (str,list):    Data rate mode(s). Options include slow, fast, srvy, brst
        level   (str,list):    Data level(s). Options include l1a, l1b, l2pre, l2, l3
        tstart  (str,list):    Start time of data file. In general, the format is
                               YYYYMMDDhhmmss for "brst" mode and YYYYMMDD for "srvy"
                               mode (though there are exceptions). If not given, the
                               default is "*".
        version (str,list):    File version, formatted as "X.Y.Z", where X, Y, and Z
                               are integer version numbers.
        optdesc (str,list):    Optional file name descriptor. If multiple parts,
                               they should be separated by hyphens ("-"), not under-
                               scores ("_").
    
    Returns:
        fnames  (str,list);    File names constructed from inputs.
    """
    
    # Convert all to lists
    if isinstance(sc, str):
        sc = [sc]
    if isinstance(instr, str):
        instr = [instr]
    if isinstance(mode, str):
        mode = [mode]
    if isinstance(level, str):
        level = [level]
    if isinstance(tstart, str):
        tstart = [tstart]
    if isinstance(version, str):
        version = [version]
    if optdesc is not None and isinstance(optdesc, str):
        optdesc = [optdesc]
    
    # Accept tuples, as those returned by MrMMS_Construct_Filename
    if type(sc) == 'tuple':
        sc_ids = [file[0] for file in sc]
        instr = [file[1] for file in sc]
        mode = [file[2] for file in sc]
        level = [file[3] for file in sc]
        tstart = [file[-2] for file in sc]
        version = [file[-1] for file in sc]
        
        if len(sc) > 6:
            optdesc = [file[4] for file in sc]
        else:
            optdesc = None
    else:
        sc_ids = sc
    
    
    if optdesc is None:
        fnames = ['_'.join((s,i,m,l,t,'v'+v+'.cdf')) for s in sc_ids
                                                     for i in instr
                                                     for m in mode
                                                     for l in level
                                                     for t in tstart
                                                     for v in version]
    else:
        fnames = ['_'.join((s,i,m,l,o,t,'v'+v+'.cdf')) for s in sc_ids
                                                       for i in instr
                                                       for m in mode
                                                       for l in level
                                                       for o in optdesc
                                                       for t in tstart
                                                       for v in version]
    return fnames



def construct_path(sc, instr=None, mode=None, level=None, tstart='*',
                   optdesc=None, root='', files=False):
    """
    Construct a directory structure compliant with MMS path guidelines.
    
    MMS paths follow the convention
        brst: sc/instr/mode/level[/optdesc]/<year>/<month>/<day>
        srvy: sc/instr/mode/level[/optdesc]/<year>/<month>
    
    Arguments:
        sc (str,list,tuple):   Spacecraft ID(s)
        instr   (str,list):    Instrument ID(s)
        mode    (str,list):    Data rate mode(s). Options include slow, fast, srvy, brst
        level   (str,list):    Data level(s). Options include l1a, l1b, l2pre, l2, l3
        tstart  (str,list):    Start time of data file, formatted as a date: '%Y%m%d'.
                               If not given, all dates from 20150901 to today's date are
                               used.
        optdesc (str,list):    Optional file name descriptor. If multiple parts,
                               they should be separated by hyphens ("-"), not under-
                               scores ("_").
        root    (str):         Root directory at which the directory structure begins.
        files   (bool):        If True, file names will be generated and appended to the
                               paths. The file tstart will be "YYYYMMDD*" (i.e. the date
                               with an asterisk) and the version number will be "*".
    
    Returns:
        fnames  (str,list);    File names constructed from inputs.
    """
    
    # Convert all to lists
    if isinstance(sc, str):
        sc = [sc]
    if isinstance(instr, str):
        instr = [instr]
    if isinstance(mode, str):
        mode = [mode]
    if isinstance(level, str):
        level = [level]
    if isinstance(tstart, str):
        tstart = [tstart]
    if optdesc is not None and isinstance(optdesc, str):
        optdesc = [optdesc]
    
    # Accept tuples, as those returned by MrMMS_Construct_Filename
    if type(sc) == 'tuple':
        sc_ids = [file[0] for file in sc]
        instr = [file[1] for file in sc]
        mode = [file[2] for file in sc]
        level = [file[3] for file in sc]
        tstart = [file[-2] for file in sc]
        
        if len(sc) > 6:
            optdesc = [file[4] for file in sc]
        else:
            optdesc = None
    else:
        sc_ids = sc
    
    # Paths + Files
    if files:
        if optdesc is None:
            paths = [os.path.join(root,s,i,m,l,t[0:4],t[4:6],t[6:8],'_'.join((s,i,m,l,t+'*','v*.cdf'))) if m == 'brst' else
                     os.path.join(root,s,i,m,l,t[0:4],t[4:6],'_'.join((s,i,m,l,t+'*','v*.cdf')))
                     for s in sc_ids
                     for i in instr
                     for m in mode
                     for l in level
                     for t in tstart]
        else:
            paths = [os.path.join(root,s,i,m,l,o,t[0:4],t[4:6],t[6:8],'_'.join((s,i,m,l,o,t+'*','v*.cdf'))) if m == 'brst' else
                     os.path.join(root,s,i,m,l,o,t[0:4],t[4:6],'_'.join((s,i,m,l,o,t+'*','v*.cdf')))
                     for s in sc_ids
                     for i in instr
                     for m in mode
                     for l in level
                     for o in optdesc
                     for t in tstart]
    
    # Paths
    else:
        if optdesc is None:
            paths = [os.path.join(root,s,i,m,l,t[0:4],t[4:6],t[6:8]) if m == 'brst' else
                     os.path.join(root,s,i,m,l,t[0:4],t[4:6]) for s in sc_ids
                                                              for i in instr
                                                              for m in mode
                                                              for l in level
                                                              for t in tstart]
        else:
            paths = [os.path.join(root,s,i,m,l,o,t[0:4],t[4:6],t[6:8]) if m == 'brst' else
                     os.path.join(root,s,i,m,l,o,t[0:4],t[4:6]) for s in sc_ids
                                                                for i in instr
                                                                for m in mode
                                                                for l in level
                                                                for o in optdesc
                                                                for t in tstart]
    
    
    return paths


def filename2path(fnames, root=''):
    """
    Convert an MMS file name to an MMS path.
    
    MMS paths take the form
        
        sc/instr/mode/level[/optdesc]/YYYY/MM[/DD/]
        
    where the optional descriptor [/optdesc] is included if it is also in the
    file name and day directory [/DD] is included if mode='brst'.
    
    Arguments:
        fnames (str,list):    File names to be turned into paths.
        root   (str):     Absolute directory
    
    Returns:
        paths (list):     Path to the data file.
    """
    
    paths = []
    
    # Convert input file names to an array
    if type(fnames) is str:
        fnames = [fnames]
    
    parts = parse_filename(fnames)
    
    for idx, part in enumerate(parts):
        # Create the directory structure
        #   sc/instr/mode/level[/optdesc]/YYYY/MM/
        path = os.path.join(root, *part[0:5], part[5][0:4], part[5][4:6])
        
        # Burst files require the DAY directory
        #   sc/instr/mode/level[/optdesc]/YYYY/MM/DD/
        if part[3] == 'brst':
            path = os.path.join(path, part[5][6:8])
        
        # Append the filename
        path = os.path.join(path, fnames[idx])
        paths.append(path)
    
    return paths


def filter_time(fnames, start_date, end_date):
    """
    Filter files by their start times.
    
    Arguments:
        fnames (str,list):    File names to be filtered.
        start_date (str):     Start date of time interval, formatted as '%Y-%m-%dT%H:%M:%S'
        end_date (str):       End date of time interval, formatted as '%Y-%m-%dT%H:%M:%S'
    
    Returns:
        paths (list):     Path to the data file.
    """
    
    # Output
    files = fnames
    if isinstance(files, str):
        files = [files]
    
    # Convert date range to datetime objects
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
    
    # Parse the time out of the file name
    parts = parse_file_name(fnames)
    fstart = [dt.datetime.strptime(name[-2], '%Y%m%d') if len(name[-2]) == 8 else
              dt.datetime.strptime(name[-2], '%Y%m%d%H%M%S')
              for name in parts]
    
    # Sor the files by start time
    isort = sorted(range(len(fstart)), key=lambda k: fstart[k])
    fstart = [fstart[i] for i in isort]
    files = [files[i] for i in isort]
    
    # End time
    #   - Any files that start on or before END_DATE can be kept
    idx = [i for i, t in enumerate(fstart) if t <= end_date ]
    if len(idx) > 0:
        fstart = [fstart[i] for i in idx]
        files = [files[i] for i in idx]
    else:
        fstart = []
        files = []
    
    # Start time
    #   - Any file with TSTART <= START_DATE can potentially have data
    #     in our time interval of interest.
    #   - Assume the start time of one file marks the end time of the previous file.
    #   - With this, we look for the file that begins just prior to START_DATE and
    #     throw away any files that start before it.
#    idx = [i for i, t in enumerate(fstart) if t.date() < start_date.date()]
    idx = [i for i, t in enumerate(fstart) if t >= start_date]

    if (len(idx) == 0) & (fstart[-1].date() == start_date.date()):
        idx = [len(fstart)-1]
    elif (len(idx) != 0) & ((idx[0] != 0) & (fstart[idx[0]] != start_date)):
        idx.insert(0, idx[0]-1)
    
    if len(idx) > 0:
        fstart = [fstart[i] for i in idx]
        files = [files[i] for i in idx]
    else:
        fstart = []
        files = []
    
    return files


def filter_version(files, latest=None, version=None, min_version=None):
    """
    Filter file names according to their version numbers.
    
    Arguments:
        files (str,list):    File names to be turned into paths.
        latest (bool):       If True, the latest version of each file type is returned.
                             if `version` and `min_version` are not set, this is the
                             default.
        version (str):       Only files with this version are returned.
        min_version (str):   All files with version greater or equal to this are returned.
    
    Returns:
        filtered_files (list):     The files remaining after applying filter conditions.
    """
    
    if version is None and min is None:
        latest = True
    if (version == None + min_version == None + latest == None) > 1:
        ValueError('latest, version, and min are mutually exclusive.')
    
    # Output list
    filtered_files = []
    
    # The latest version of each file type
    if latest:
        # Parse file names and identify unique file types
        #   - File types include all parts of file name except version number
        parts = mms_parse_filename(files)
        bases = ['_'.join(part[0:-2]) for part in parts]
        versions = [part[-1] for part in parts]
        uniq_bases = list(set(bases))
        
        # Filter according to unique file type
        for idx, uniq_base in enumerate(uniq_bases):
            test_idx = [i for i, test_base in bases if test_base == uniq_base]
            file_ref = files[idx]
            vXYZ_ref = versions[idx].split('.')
        
            filtered_files.append(file_ref)
            for i in test_idx:
                vXYZ = versions[i].split('.')
                if ( (vXYZ[0] > vXYZ_ref[0]) or
                     (vXYZ[0] == vXYZ_ref[0] and vXYZ[1] > vXYZ_ref[1]) or
                     (vXYZ[0] == vXYZ_ref[0] and vXYZ[1] == vXYZ_ref[1] and vXYZ[2] > vXYZ_ref[2])
                   ):
                    filtered_files[-1] = files[i]
    
    # All files with version number greater or equal to MIN_VERSION
    elif min_version is not None:
        vXYZ_min = min_version.split('.')
        for idx, v in enumerate(versions):
            vXYZ = v.split('.')
            if ( (vXYZ[0] > vXYZ_min[0]) or 
                 (vXYZ[0] == vXYZ_min[0] and vXYZ[1] > vXYZ_min[1]) or
                 (vXYZ[0] == vXYZ_min[0] and vXYZ[1] == vXYZ_min[1] and vXYZ[2] >= vXYZ_min[2])
               ):
                filtered_files.append(files[idx])
    
    # All files with a particular version number
    elif version is not None:
        vXYZ_ref = min_version.split('.')
        for idx, v in enumerate(versions):
            vXYZ = v.split('.')
            if (vXYZ[0] == vXYZ_ref[0] and
                vXYZ[1] == vXYZ_ref[1] and
                vXYZ[2] == vXYZ_ref[2]
               ):
                filtered_files.append(files[idx])
    
    return filtered_files


def parse_file_name(fnames):
    """
    Construct a file name compliant with MMS file name format guidelines.
    
    Arguments:
        fname (str,list): File names to be parsed.
    
    Returns:
        parts (list):     A list of tuples. The tuple elements are:
                          [0]: Spacecraft IDs
                          [1]: Instrument IDs
                          [2]: Data rate modes
                          [3]: Data levels
                          [4]: Optional descriptor (empty string if not present)
                          [5]: Start times
                          [6]: File version number
    """
    
    # Allocate space
    out = []
    
    if type(fnames) is str:
        files = [fnames]
    else:
        files = fnames
    
    # Parse each file
    for file in files:
        # Parse the file names
        parts = os.path.basename(file).split('_')
        
        if len(parts) == 6:
            optdesc = ''
        else:
            optdesc = parts[4]
            
        out.append((*parts[0:4], optdesc, parts[-2], parts[-1][1:-4]))
    
    return out


def parse_time(times):
    """
    Parse the start time of MMS file names.
    
    Arguments:
        times (str,list): Start times of file names.
    
    Returns:
        parts (list):     A list of tuples. The tuple elements are:
                          [0]: Year
                          [1]: Month
                          [2]: Day
                          [3]: Hour
                          [4]: Minute
                          [5]: Second
    """
    
    if isinstance(times, str):
        times = [times]
    
    # Two types: srvy=YYYYMMDD and brst=YYYYMMDDhhmmss
    #   - Accessing "hhmmss" of srvy times returns empty strings, not errors
    parts = [(time[0:4], time[4:6], time[6:8], time[8:10], time[10:12], time[12:14]) for time in times]
    
    return parts


def sort_files(files):
    """
    Sort MMS file names by data product and time.
    
    Arguments:
        files (str,list):   Files to be sorted
    
    Returns:
        sorted (tuple):     Sorted file names. Each tuple element corresponds to
                            a unique data product.
    """
    
    # File types and start times
    parts = parse_file_name(files)
    bases = ['_'.join(p[0:5]) for p in parts]
    tstart = [p[-2] for p in parts]
    
    # Sort everything
    idx = sorted(range(len(tstart)), key=lambda k: tstart[k])
    bases = [bases[i] for i in idx]
    files = [files[i] for i in idx]
    
    # Find unique file types
    fsort = []
    uniq_bases = list(set(bases))
    for ub in uniq_bases:
        fsort.append([files[i] for i, b in enumerate(bases) if b == ub])
        
    return tuple(fsort)







def _validate_instrument(instrument):
    allowed_instruments = ['afg', 'aspoc', 'dfg', 'dsp', 'edi',
                           'edp', 'fgm', 'fpi', 'fields', 'scm', 'sdp', ]
    if instrument not in allowed_instruments:
        raise ValueError(
            'Instrument {} not in list of allowed instruments: {}'.format(
                instrument, allowed_instruments))


def _validate_probe(probe):
    allowed_probes = [str(i+1) for i in range(4)]
    probe = str(probe)
    if probe not in allowed_probes:
        raise ValueError(
            'Probe {} not in list of allowed probes: {}'.format(
                probe, allowed_probes))
    return probe


def _validate_data_rate(data_rate):
    allowed_rates = ['slow', 'fast', 'brst', 'srvy', '']
    if data_rate not in allowed_rates:
        raise ValueError(
            'Data rate {} not in list of allowed data rates: {}'.format(
                data_rate, allowed_rates))


def available_files(probe, instrument, starttime, endtime, data_rate=''):
    """
    Get available MMS files as a list.

    See the "Query paramters" section of
    https://lasp.colorado.edu/mms/sdc/public/about/how-to/ for more information
    on the query paramters.

    Parameters
    ----------
    probe : int or str
        MMS probe number. Must be in 1-4 inclusive.
    instrument : str
        MMS instrument. Must be in ``['afg', 'aspoc', 'dfg', 'dsp', 'edi',
        'edp', 'fields', 'scm', 'sdp']``
    starttime : ~datetime.datetime
        Start time.
    endtime : ~datetime.datetime
        End time.
    data_rate : str, optional
        Data rate. Must be in ``['slow', 'fast', 'brst', 'srvy']``

    Returns
    -------
    list
        List of file names.
    """
    _validate_instrument(instrument)
    probe = _validate_probe(probe)
    _validate_data_rate(data_rate)
    start_date = starttime.strftime('%Y-%m-%d')
    end_date = endtime.strftime('%Y-%m-%d')

    query = {}
    query['sc_id'] = 'mms' + probe
    query['instrument_id'] = instrument
    if len(data_rate):
        query['data_rate_mode'] = data_rate
    query['start_date'] = start_date
    query['end_date'] = end_date

    r = requests.get(query_url, params=query)
    files = r.text.split(',')
    return files


def download_files(probe, instrument, data_rate, starttime, endtime,
                   verbose=True, product_string='', warn_missing_units=True):
    """
    Download MMS files.

    Parameters
    ----------
    probe : int or str
        MMS probe number. Must be in 1-4 inclusive.
    instrument : str
        MMS instrument. Must be in ``['afg', 'aspoc', 'dfg', 'dsp', 'edi',
        'edp', 'fields', 'scm', 'sdp']``
    data_rate : str
        Data rate. Must be in ``['slow', 'fast', 'brst', 'srvy']``
    starttime : ~datetime.datetime
        Start time.
    endtime : ~datetime.datetime
        End time.
    verbose : bool, optional
        If ``True``, show a progress bar while downloading.
    product_string : str, optional
        If not empty, this string must be in the filename for it to be
        downloaded.
    warn_missing_units : bool, optional
        If ``True``, warnings will be shown for each variable that does not
        have associated units.

    Returns
    -------
    df : :class:`~sunpy.timeseries.GenericTimeSeries`
        Requested data.
    """
    _validate_instrument(instrument)
    probe = _validate_probe(probe)

    dirs = []
    fnames = []
    daylist = util._daysplitinterval(starttime, endtime)
    for date, stime, etime in daylist:
        files = available_files(probe, instrument,
                                starttime, endtime, data_rate)
        for file in files:
            fname = pathlib.Path(file).stem
            if product_string in fname and len(fname):
                fnames.append(fname)
                dirs.append('')

    extension = '.cdf'
    local_base_dir = mms_dir / probe / instrument / data_rate
    remote_base_url = dl_url

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
            url = remote_base_url + '?file=' + fname + extension
            local_fname = os.path.join(local_base_dir, fname + extension)
            with requests.get(url, stream=True) as request:
                with open(local_fname, 'wb') as fd:
                    for chunk in tqdm(
                            request.iter_content(chunk_size=128)):
                        fd.write(chunk)

    def processing_func(cdf):
        return util.cdf2df(cdf, index_key='Epoch')

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime,
                        warn_missing_units=warn_missing_units)


def _fpi_docstring(product):
    return """
Import fpi {} data.

Parameters
----------
probe : string
    Probe number, must be 1, 2, 3, or 4
mode : string
    Data mode, must be 'fast' or 'brst'
starttime : datetime
    Interval start time.
endtime : datetime
    Interval end time.

Returns
-------
data : :class:`~sunpy.timeseries.TimeSeries`
    Imported data.
""".format(product)


def fpi_dis_moms(probe, mode, starttime, endtime):
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='dis-moms')


fpi_dis_moms.__doc__ = _fpi_docstring('ion distribution moment')


def fpi_des_moms(probe, mode, starttime, endtime):
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='des-moms')


fpi_des_moms.__doc__ = _fpi_docstring('electron distribution moment')


def fpi_dis_dist(probe, mode, starttime, endtime):
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='dis-dist', warn_missing_units=False)


fpi_dis_dist.__doc__ = _fpi_docstring('ion distribution function')


def fpi_des_dist(probe, mode, starttime, endtime):
    return download_files(probe, 'fpi', mode, starttime, endtime,
                          product_string='des-dist', warn_missing_units=False)


fpi_des_dist.__doc__ = _fpi_docstring('electron distribution function')


def fgm(probe, mode, starttime, endtime):
    """
    Import fgm survey mode magnetic field data.

    Parameters
    ----------
    probe : string
        Probe number, must be 1, 2, 3, or 4
    mode : str
        Data rate.
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Imported data.
    """
    return download_files(probe, 'fgm', mode, starttime, endtime)
