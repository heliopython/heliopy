"""
Methods for importing data from the four MMS spacecraft.

All data is publically available at
https://lasp.colorado.edu/mms/sdc/public/data/, and the MMS science data centre
is at https://lasp.colorado.edu/mms/sdc/public/.
"""
import os
import pathlib
import glob
import datetime as dt
import re
import requests
import tqdm.auto as tqdm
import urllib
import urllib3
import pdb
import io
import csv
import pathlib
import warnings

import heliopy
from heliopy.data import util
import sunpy.time
import scipy.io
from cdflib import epochs
import numpy as np

data_dir = pathlib.Path(heliopy.config['download_dir'])
sdc_username = heliopy.config['mms_username']
sdc_password = heliopy.config['mms_password']
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
        """
        Initialization method

        Parameters
        ----------
        sc : str, list
            Spacecraft ID.
        instr : str, list
            Instrument ID.
        mode : str, list
            Data rate mode.
        level : str, list
            Data product quality level. Setting level to None, "l2", or "l3"
            automatically sets site to "public".
        anc_product : bool
            Set to True if you want ancillary data. Automatically sets
            "data_type" to "ancillary".
        data_type : str
            Type of information requested from the SDC:
                "science" - Science data
                "hk" - Housekeeping data
                "ancillary" - attitude and emphemeris data
                "abs_selections" - Automated burst segment selections
                "sitl_selections" - Burst selections made by the SITL
                "gls_selections_*" - Burst selections made by the ground loop
        data_root : str
            Root directory in which to download MMS data. Additional
            directories beyond data_root are created to mimic the MMS
            file system structure. Defaults to heliopy.config['download_dir'].
        dropbox_root : str
            Directory in which newly created data files are temporarily saved.
            In the MMS data processing flow, newly created data files are
            stored in dropbox_dir. After data file validation, they are
            removed from dropbox_dir and placed in data_root.
        end_date : str, `datetime.datetime`
            End time of data interval of interest. If a string, it must be in
            ISO-8601 format: YYYY-MM-DDThh:mm:ss, and is subsequently
            converted to a datetime object.
        files : str
            Name of the specific file or files to download. Automatically sets
            sd, instr, mode, level, optdesc, and version attributes to None.
        mirror_root : str
            Root directory of an MMS mirror site, in case certain data
            products are automatically rsynced to a local server.
        offline : bool
            If True, file information will be gathered from the local file
            system only (i.e. no requests will be posted to the SDC).
        optdesc : str, list
            Optional descriptor of the data products.
        site : str
            Indicate that requests should be posted to the public or private
            side of the SDC. The private side needs team log-in credentials.
                "public" - access the public side.
                "private" - access the private side.
        start_date : str, `datetime.datetime`
            Start time of data interval of interest. If a string, it must be
            in ISO-8601 format: YYYY-MM-DDThh:mm:ss, and is subsequently
            converted to a datetime object.
        version : str, list
            File version number. The format is X.Y.Z, where X, Y, and Z, are
            the major, minor, and incremental version numbers.

        Returns
        -------
        obj : `heliopy.data.mms.MMSDownloader`
            An object instance to interface with the MMS Science Data Center.
        """

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
        if data_root is None:
            data_root = pathlib.Path(heliopy.config['download_dir']) / 'mms'

        self.data_root = data_root
        self._sdc_home = 'https://lasp.colorado.edu/mms/sdc'
        self._info_type = 'download'

        # Create a persistent session
        self._session = requests.Session()
        self._session.auth = (sdc_username, sdc_password)

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
            if 'gls_selections' in value:
                if value[15:] not in ('mp-dl-unh',):
                    raise ValueError('Unknown GLS Selections type.')
            elif value not in ('ancillary', 'hk', 'science',
                               'abs_selections', 'sitl_selections'
                               ):
                raise ValueError('Invalid value {} for attribute'
                                 ' "{}".'.format(value, name))

            # Unset attributes related to data_type = 'science'
            if 'selections' in value:
                self.sc = None
                self.instr = None
                self.mode = None
                self.level = None
                self.optdesc = None
                self.version = None

        elif name == 'files':
            if value is not None:
                self.sc = None
                self.instr = None
                self.mode = None
                self.level = None
                self.optdesc = None
                self.version = None

        elif name == 'level':
            # L2 and L3 are the only public data levels
            if value in [None, 'l2', 'l3']:
                self.site = 'public'
            else:
                self.site = 'private'

        elif name == 'site':
            # Team site is most commonly referred to as the "team",
            # or "private" site, but in the URL is referred to as the
            # "sitl" site. Accept any of these values.
            if value in ['private', 'team', 'sitl']:
                value = 'sitl'
            elif value == 'public':
                value = 'public'
            else:
                raise ValueError('Invalid value for attribute {}.'
                                 .format(name)
                                 )

        elif name in ('start_date', 'end_date'):
            # Convert string to datetime object
            if isinstance(value, str):
                try:
                    value = dt.datetime.strptime(value[0:19],
                                                 '%Y-%m-%dT%H:%M:%S'
                                                 )
                except ValueError:
                    try:
                        value = dt.datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        raise

        # Set the value
        super(MMSDownloader, self).__setattr__(name, value)

    def intervals(self):
        """
        The complete list of sub-intervals that cover a time range
        Each sub-interval is associated with a single file to be downloaded and
        read in.

        Parameters
        ----------
        starttime : datetime.datetime
            Start time of interval within which data sub-intervals are
            determined.
        endtime : datetime.datetime
            End time of interval within which data sub-intervals are
            determined.

        Returns
        -------
        intervals : list of sunpy.time.TimeRange
            List of intervals
        """

        # Start time from file names
        fnames = self.file_names()
        nfiles = len(fnames)
        parts = parse_file_names(fnames)

        # MMS files do not have end times in their file names and burst files
        # do not have a fixed start time or duration (although survey files
        # do). Assume the end time of one file is a microsecond before the
        # start time of the next file in sequence (or the end of the time
        # interval, if sooner). Step through files backwards, since end[i-1]
        # depends on start[i].
        trange = [None]*nfiles
        for i in range(nfiles-1, -1, -1):
            # Start tiem of interval
            if len(parts[i][5]) == 8:
                start = dt.datetime.strptime(parts[i][5], '%Y%m%d')
            else:
                start = dt.datetime.strptime(parts[i][5], '%Y%m%d%H%M%S')

            # End time of interval. Subtract one second to prevent the file
            # that begins at trange[i+1] is not included in any results.
            if i == (nfiles-1):
                end = self.end_date
            elif i >= 0:
                end = trange[i+1].start - dt.timedelta(seconds=1)

            trange[i] = sunpy.time.TimeRange(start, end)

        return trange

    def local_dir(self, interval=None):
        """
        Local directory for a given interval. The interval should correspond
        to a single data file (i.e. a single interval returned by
        self.intervals).

        Parameters
        ----------
        interval : sunpy.time.TimeRange

        Returns
        -------
        dir : pathlib.Path
            Local directory
        """

        # Create a list of sequential dates spanning the time interval
        date = interval.start.to_datetime().strftime('%Y%m%d')

        # Create the local directories
        dir = construct_path(self.sc, self.instr, self.mode, self.level, date,
                             optdesc=self.optdesc, root=self.data_root)
        return dir[0]

    def fname(self, interval, mirror=False):
        """
        Return the filename for a given interval from the SDC.

        Parameters
        ----------
        interval : sunpy.time.TimeRange

        Returns
        -------
        fname : str
            Filename
        """

        # File names have version numbers in them. To get the most recent
        # version, we must go through the SDC. Most functions key off the
        # larger time interval of interest, so we must temporarily set it
        # to the interval of a single data file.
        interval_in = self.get_interval()
        self.set_interval(interval)

        # Get the file name
        try:
            file = self.fnames()
            file = filter_time(file,
                               interval.start.to_datetime(),
                               interval.end.to_datetime()
                               )

            # Filter to within given interval.
            if len(file) == 1:
                file = file[0]
            elif len(file) > 1:
                ValueError('More than one file found. '
                           'Restrict interval or use fnames().')
        except IndexError:
            file = ''

        # Reset the time interval
        self.set_interval(interval_in)

        return file

    @staticmethod
    def datetime2interval(start_date, end_date):
        """
        Convert datetimes to a sunpy TimeRange instance.

        Parameters
        ----------
        start_date : datetime
            Start time of interval
        end_Date : End time of interval

        Returns
        ----------
        interval : sunpy.time.TimeRange
            Start and end time of the data interval
        """
        return sunpy.time.TimeRange(start_date, end_date)

    def get_interval(self):
        """
        Get the time interval of interest.

        Returns
        ----------
        interval : sunpy.time.TimeRange
            Start and end time of the data interval
        """
        return self.datetime2interval(self.start_date, self.end_date)

    def set_interval(self, interval):
        """
        Set the time interval of interest.

        Parameters
        ----------
        interval : sunpy.time.TimeRange
            Start and end time of the data interval
        """
        self.start_date = interval.start.to_datetime()
        self.end_date = interval.end.to_datetime()

    def download(self, interval):
        """
        Download a file corresponding to a given interval.

        Parameters
        ----------
        interval : sunpy.time.TimeRange
            Time interval for which to download data.

        Returns
        -------
        file : str
            Full path of the downloaded data file.
        """

        # File names have version numbers in them. To get the most recent
        # version, we must go through the SDC. Most functions key off the
        # larger time interval of interest, so we must temporarily set it to
        # the interval of a single data file.
        interval_in = self.get_interval()
        self.set_interval(interval)

        try:
            file = self.download_files()[0]
        except IndexError:
            file = ''

        self.set_interval(interval_in)
        return file

    def load_local_file(self, interval):
        """
        Load a local file

        Parameters
        ----------
        interval : sunpy.time.TimeRange
            Time interval of data to be loaded.

        Returns
        -------
        pandas.DataFrame
        """

        local_path = os.path.join(self.local_dir(interval),
                                  self.fname(interval)
                                  )
        cdf = util._load_cdf(local_path)
        return util.cdf2df(cdf, index_key='Epoch')

    def fnames(self):
        """
        Obtain file names from the SDC.

        NOTE: The SDC API is lenient on file start times
              and the retured list of files may be more
              inclusive than desired. Use the filter_time
              function to hone in on the desired time range.

        Returns
        -------
        files : list
            File names.
        """

        # File names have version numbers in them. To get the most recent
        # version, call out to the SDC.
        files = self.file_names()
        files = [file.split('/')[-1] for file in files]
        return files

    def url(self, query=True):
        """
        Build a URL to query the SDC.

        Parameters
        ----------
        query : bool
            If True (default), add the query string to the url.

        Returns
        -------
        url : str
            URL used to retrieve information from the SDC.
        """
        sep = '/'
        url = sep.join((self._sdc_home, self.site, 'files', 'api', 'v1',
                        self._info_type, self.data_type))

        # Build query from parts of file names
        if query:
            query_string = '?'
            qdict = self.query()
            for key in qdict:
                query_string += key + '=' + qdict[key] + '&'

            # Combine URL with query string
            url += query_string

        return url

    def check_response(self, response):
        '''
        Check the status code for a requests response and perform
        and appropriate action (e.g. log-in, raise error, etc.)

        Parameters
        ----------
        response : `requests.response`
            Response from the SDC

        Returns
        -------
        r : `requests.response`
            Updated response
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
                #   - However, the prepared request lacks the
                #     authentication data
                if response.request.method == 'POST':
                    query = urllib.parse.parse_qs(response.request.body)
                    r = self._session.post(response.request.url, data=query)
                else:
                    r = self._session.get(response.request.url)

                # Another attempt
                if r.ok:
                    break
                else:
                    print('Incorrect username or password. %d tries '
                          'remaining.' % maxAttempts-nAttemps)
                    nAttempts += 1

            # Failed log-in
            if nAttempts > maxAttempts:
                raise ConnectionError('Failed log-in.')

        else:
            raise ConnectionError(response.reason)

        # Return the resulting request
        return r

    def download_from_sdc(self, file_names):
        '''
        Download multiple files from the SDC. To prevent downloading the
        same file multiple times and to properly filter by file start time
        see the download_files method.

        Parameters
        ----------
        file_names : str, list
            File names of the data files to be downloaded. See
            the file_names method.

        Returns
        -------
        local_files : list
            Names of the local files. Remote files downloaded
            only if they do not already exist locally
        '''

        # Make sure files is a list
        if isinstance(file_names, str):
            file_names = [file_names]

        # Get information on the files that were found
        #   - To do that, specify the specific files.
        #     This sets all other properties to None
        #   - Save the state of the object as it currently
        #     is so that it can be restored
        #   - Setting FILES will indirectly cause SITE='public'.
        #     Keep track of SITE.
        site = self.site
        state = {}
        state['sc'] = self.sc
        state['instr'] = self.instr
        state['mode'] = self.mode
        state['level'] = self.level
        state['optdesc'] = self.optdesc
        state['version'] = self.version
        state['files'] = self.files

        # Build the URL sans query
        self.site = site
        self._info_type = 'download'
        self.files = file_names
        url = '/'.join((self._sdc_home, self.site, 'files', 'api', 'v1',
                        self._info_type, self.data_type))

        # Get file name and size
        file_info = self.file_info()

        # Amount to download per iteration
        block_size = 1024*128
        local_file_names = []

        # Download each file individually
        for info in file_info['files']:
            # Create the destination directory
            file = self.name2path(info['file_name'])
            if not os.path.isdir(os.path.dirname(file)):
                os.makedirs(os.path.dirname(file))

            # Download data with progress bar
            try:
                r = self._session.get(url,
                                      params={'file': info['file_name']},
                                      stream=True)
                with tqdm.tqdm(total=info['file_size'],
                               unit='B',
                               unit_scale=True,
                               unit_divisor=1024
                               ) as pbar:
                    with open(file, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=block_size):
                            if chunk:  # filter out keep-alive new chunks
                                f.write(chunk)
                                pbar.update(block_size)
            except:
                if os.path.isfile(file):
                    os.remove(file)
                for key in state:
                    self.files = None
                    setattr(self, key, state[key])
                raise

            local_file_names.append(file)

        # Restore the entry state
        self.files = None
        for key in state:
            setattr(self, key, state[key])

        return local_file_names

    def file_info(self):
        '''
        Obtain file information from the SDC.

        Returns
        -------
        file_info : list
            Information about each file.
        '''
        self._info_type = 'file_info'
        response = self.get()
        return response.json()

    def file_names(self):
        '''
        Obtain file names from the SDC. Note that the SDC accepts only
        start and end dates, not datetimes. Therefore the files returned
        by this function may lie outside the time interval of interest.
        For a more precise list of file names, use the search method or
        filter the files with filter_time.

        Returns
        -------
        file_names : list
            Names of the requested files.
        '''
        self._info_type = 'file_names'
        response = self.get()

        if response.text == '':
            return []
        else:
            return response.text.split(',')

    def get(self):
        '''
        Retrieve information from the SDC.

        Returns
        -------
        r : `session.response`
            Response to the request posted to the SDC.
        '''
        # Build the URL sans query
        url = self.url(query=False)

        # Check on query
        r = self._session.get(url, params=self.query())

        # Check if everything is ok
        if not r.ok:
            r = self.check_response(r)

        # Return the response for the requested URL
        return r

    def download_files(self):
        '''
        Download files from the SDC. First, search the local file
        system to see if they have already been downloaded.

        Returns
        -------
        local_files : list
            Names of the local files.
        '''

        # Get available files
        local_files, remote_files = self.search()
        if self.offline:
            return local_files

        # Download remote files
        #   - file_info() does not want the remote path
        if len(remote_files) > 0:
            remote_files = [file.split('/')[-1] for file in remote_files]
            downloaded_files = self.download_from_sdc(remote_files)
            local_files.extend(downloaded_files)

        return local_files

    def local_file_names(self, mirror=False):
        '''
        Search for MMS files on the local system. Files must be
        located in an MMS-like directory structure.

        Parameters
        ----------
        mirror : bool
            If True, the local data directory is used as the
            root directory. Otherwise the mirror directory is
            used.

        Returns
        -------
        local_files : list
            Names of the local files
        '''

        # Search the mirror or local directory
        if mirror:
            data_root = self.mirror_root
        else:
            data_root = self.data_root

        # If no start or end date have been defined,
        #   - Start at beginning of mission
        #   - End at today's date
        start_date = self.start_date
        end_date = self.end_date

        # Create all dates between start_date and end_date
        deltat = dt.timedelta(days=1)
        dates = []
        while start_date <= end_date:
            dates.append(start_date.strftime('%Y%m%d'))
            start_date += deltat

        # Paths in which to look for files
        #   - Files of all versions and times within interval
        if 'selections' in self.data_type:
            paths = construct_path(data_type=self.data_type,
                                   root=data_root, files=True)
        else:
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
        '''
        Log-In to the SDC

        Parameters
        ----------
        username (str):     Account username
        password (str):     Account password
        '''

        # Ask for inputs
        if username is None:
            username = input('username: ')
        if password is None:
            password = input('password: ')

        # Save credentials
        self._session.auth = (username, password)

    def name2path(self, filename):
        '''
        Convert remote file names to local file name.

        Directories of a remote file name are separated by the '/' character,
        as in a web address.

        Parameters
        ----------
        filename : str
            File name for which the local path is desired.

        Returns
        -------
        path : str
            Equivalent local file name. This is the location to
            which local files are downloaded.
        '''
        parts = filename.split('_')

        # burst data selection directories and file names are structured as
        #   - dirname:  sitl/[type]_selections/
        #   - basename: [type]_selections_[optdesc]_YYYY-MM-DD-hh-mm-ss.sav
        # To get year, index from end to skip optional descriptor
        if parts[1] == 'selections':
            path = os.path.join(self.data_root, 'sitl',
                                '_'.join(parts[0:2]),
                                filename)

        # Burst directories and file names are structured as:
        #   - dirname:  sc/instr/mode/level[/optdesc]/YYYY/MM/DD/
        #   - basename: sc_instr_mode_level[_optdesc]_YYYYMMDDhhmmss_vX.Y.Z.cdf
        # Index from end to catch the optional descriptor, if it exists
        elif parts[2] == 'brst':
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
        '''
        Parse an official MMS file name. MMS file names are formatted as
            sc_instr_mode_level[_optdesc]_tstart_vX.Y.Z.cdf
        where
            sc:       spacecraft id
            instr:    instrument id
            mode:     data rate mode
            level:    data level
            optdesc:  optional filename descriptor
            tstart:   start time of file
            vX.Y.Z:   file version, with X, Y, and Z version numbers

        Parameters
        ----------
        filename : str
            An MMS file name

        Returns
        -------
        parts : tuple
            A tuples ordered as
                (sc, instr, mode, level, optdesc, tstart, version)
            If opdesc is not present in the file name, the output will
            contain the empty string ('').
        '''
        parts = os.path.basename(filename).split('_')

        # If the file does not have an optional descriptor,
        # put an empty string in its place.
        if len(parts) == 6:
            parts.insert(-2, '')

        # Remove the file extension ``.cdf''
        parts[-1] = parts[-1][0:-4]
        return tuple(parts)

    def post(self):
        '''
        Retrieve data from the SDC.

        Returns
        -------
        r : `session.response`
            Response to the request posted to the SDC.
        '''
        # Build the URL sans query
        url = self.url(query=False)

        # Check on query
        r = self._session.post(url, data=self.query())

        # Check if everything is ok
        if not r.ok:
            r = self.check_response(r)

        # Return the response for the requested URL
        return r

    def query(self):
        '''
        build a dictionary of key-value pairs that serve as the URL
        query string.

        Returns
        -------
        query : dict
            URL query
        '''

        # Adjust end date
        #   - The query takes '%Y-%m-%d' but the object allows
        #     '%Y-%m-%dT%H:%M:%S'
        #   - Further, the query is half-exclusive: [start, end)
        #   - If the dates are the same but the times are different, then
        #     files between self.start_date and self.end_date will not be
        #     found
        #   - In these circumstances, increase the end date by one day
        if self.end_date is not None:
            end_date = self.end_date.strftime('%Y-%m-%d')
            if self.start_date.date() == self.end_date.date() or \
               self.end_date.time() != dt.time(0, 0, 0):
                end_date = (self.end_date + dt.timedelta(1)
                            ).strftime('%Y-%m-%d')

        query = {}
        if self.sc is not None:
            query['sc_id'] = self.sc if isinstance(self.sc, str) \
                                     else ','.join(self.sc)
        if self.instr is not None:
            query['instrument_id'] = self.instr \
                                     if isinstance(self.instr, str) \
                                     else ','.join(self.instr)
        if self.mode is not None:
            query['data_rate_mode'] = self.mode if isinstance(self.mode, str) \
                                                else ','.join(self.mode)
        if self.level is not None:
            query['data_level'] = self.level if isinstance(self.level, str) \
                                             else ','.join(self.level)
        if self.optdesc is not None:
            query['descriptor'] = self.optdesc \
                                  if isinstance(self.optdesc, str) \
                                  else ','.join(self.optdesc)
        if self.version is not None:
            query['version'] = self.version if isinstance(self.version, str) \
                                            else ','.join(self.version)
        if self.files is not None:
            query['files'] = self.files if isinstance(self.files, str) \
                                        else ','.join(self.files)
        if self.start_date is not None:
            query['start_date'] = self.start_date.strftime('%Y-%m-%d')
        if self.end_date is not None:
            query['end_date'] = end_date

        return query

    def remote2localnames(self, remote_names):
        '''
        Convert remote file names to local file names.

        Directories of a remote file name are separated by the '/' character,
        as in a web address.

        Parameters
        ----------
        remote_names : list
            Remote file names returned by FileNames.

        Returns
        -------
        local_names : list
            Equivalent local file name. This is the location to
            which local files are downloaded.
        '''
        # os.path.join() requires string arguments
        #   - str.split() return list.
        #   - Unpack with *
        local_names = list()
        for file in remote_names:
            local_names.append(os.path.join(self.data_root,
                               *file.split('/')[2:]))

        if (len(remote_names) == 1) & (type(remote_names) == 'str'):
            local_names = local_names[0]

        return local_names

    def search(self):
        '''
        Search for files locally and at the SDC.

        Returns
        -------
        files : tuple
            Local and remote files within the interval, returned as
            (local, remote), where `local` and `remote` are lists.
        '''

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
            idx = [i for i, local in enumerate(local_files)
                   if os.path.isfile(local)
                   ]

            # Filter based on location
            local_files = [local_files[i] for i in idx]
            remote_files = [remote_files[i] for i in range(len(remote_files))
                            if i not in idx
                            ]

        # Filter based on time interval
        if len(local_files) > 0:
            local_files = filter_time(local_files,
                                      self.start_date,
                                      self.end_date
                                      )
        
        if len(remote_files) > 0:
            remote_files = filter_time(remote_files,
                                       self.start_date,
                                       self.end_date
                                       )

        return (local_files, remote_files)

    def version_info(self):
        '''
        Obtain version information from the SDC.

        Returns
        -------
        vinfo : dict
            Version information regarding the requested files
        '''
        self._info_type = 'version_info'
        response = self.post()
        return response.json()


def _datetime_to_list(datetime):
    return [datetime.year, datetime.month, datetime.day,
            datetime.hour, datetime.minute, datetime.second,
            datetime.microsecond // 1000, datetime.microsecond % 1000, 0
            ]


def burst_data_segments(start_date, end_date, team=False):
    """
    Get information about burst data segments.

    Parameters
    ----------
    start_date : `datetime`
        Start date of time interval for which information is desired.
    end_date : `datetime`
        End date of time interval for which information is desired.
    team : bool=False
        If set, information will be taken from the team site
        (login required). Otherwise, it is take from the public site.

    Returns
    -------
    data : dict
        Dictionary of information about burst data segments
            =============     ==========
            Key               Definition
            =============     ==========
            DATASEGMENTID
            TAISTARTTIME      Start time of burst segment in
                              TAI sec since 1958-01-01
            TAIENDTIME        End time of burst segment in
                              TAI sec since 1958-01-01
            PARAMETERSETID
            FOM               Figure of merit given to the burst segment
            ISPENDING
            INPLAYLIST
            STATUS            Download status of the segment
            NUMEVALCYCLES
            SOURCEID          Username of SITL who selected the segment
            CREATETIME        ? as datetime
            FINISHTIME        ? as datetime
            OBS1NUMBUFS
            OBS2NUMBUFS
            OBS3NUMBUFS
            OBS4NUMBUFS
            OBS1ALLOCBUFS
            OBS2ALLOCBUFS
            OBS3ALLOCBUFS
            OBS4ALLOCBUFS
            OBS1REMFILES
            OBS2REMFILES
            OBS3REMFILES
            OBS4REMFILES
            DISCUSSION        Description given to segment by SITL
            DT                Duration of burst segment in seconds
            TSTART            Start time of burst segment as datetime
            TEND              End time of burst segment as datetime
            =============     ==========
    """

    # Convert times to TAI since 1958
    t0 = _datetime_to_list(start_date)
    t1 = _datetime_to_list(end_date)
    t_1958 = epochs.CDFepoch.compute_tt2000([1958, 1, 1, 0, 0, 0, 0, 0, 0])
    t0 = int((epochs.CDFepoch.compute_tt2000(t0) - t_1958) // 1e9)
    t1 = int((epochs.CDFepoch.compute_tt2000(t1) - t_1958) // 1e9)

    # URL
    url_path = 'https://lasp.colorado.edu/mms/sdc/'
    url_path += 'sitl/latis/dap/' if team else 'public/service/latis/'
    url_path += 'mms_burst_data_segment.csv'

    # Query string
    query = {}
    query['TAISTARTTIME>'] = '{0:d}'.format(t0)
    query['TAIENDTIME<'] = '{0:d}'.format(t1)

    # Post the query
    sesh = requests.Session()
    sesh.auth = (sdc_username, sdc_password)
    data = sesh.get(url_path, params=query)

    # Read first line as dict keys. Cut text from TAI keys
    data = _response_text_to_dict(data.text)

    # Convert to useful types
    types = ['int16', 'int64', 'int64', 'str', 'float32', 'int8',
             'int8', 'str', 'int32', 'str', 'datetime', 'datetime',
             'int32', 'int32', 'int32', 'int32', 'int32', 'int32',
             'int32', 'int32', 'int32', 'int32', 'int32', 'str']
    for items in zip(data, types):
        if items[1] == 'str':
            pass
        elif items[1] == 'datetime':
            data[items[0]] = [dt.datetime.strptime(value,
                                                   '%Y-%m-%d %H:%M:%S'
                                                   )
                              if value != '' else value
                              for value in data[items[0]]
                              ]
        else:
            data[items[0]] = np.asarray(data[items[0]], dtype=items[1])

    # Add useful tags
    #   - Number of seconds elapsed
    #   - TAISTARTIME as datetime
    #   - TAIENDTIME as datetime
    data['TAISTARTTIME'] = data.pop('TAISTARTTIME '
                                    '(TAI seconds since 1958-01-01)'
                                    )
    data['TAIENDTIME'] = data.pop('TAIENDTIME '
                                  '(TAI seconds since 1958-01-01)'
                                  )
    data['DT'] = data['TAIENDTIME'] - data['TAISTARTTIME']

    # NOTE! If data['TAISTARTTIME'] is a scalar, this will not work
    #       unless everything after "in" is turned into a list
    data['TSTART'] = [dt.datetime(
                         *value[0:6], value[6]*1000+value[7]
                         )
                      for value in
                      epochs.CDFepoch.breakdown_tt2000(
                          data['TAISTARTTIME']*int(1e9)+t_1958
                          )
                      ]
    data['TEND'] = [dt.datetime(
                         *value[0:6], value[6]*1000+value[7]
                         )
                    for value in
                    epochs.CDFepoch.breakdown_tt2000(
                        data['TAIENDTIME']*int(1e9)+t_1958
                        )
                    ]

    return data


def construct_file_names(*args, data_type='science', **kwargs):
    '''
    Construct a file name compliant with MMS file name format guidelines.

    MMS file names follow the convention::
    
        sc_instr_mode_level[_optdesc]_tstart_vX.Y.Z.cdf

    Parameters
    ----------
    \*\*args : dict
        Arguments to be passed along.
    data_type : str
        Type of file names to construct. Options are:
        `science` or `\*_selections`. If `science`, inputs are
        passed to `construct_science_file_names``. If
        `*_selections`, inputs are passed to
        `construct_selections_file_names`.
    \*\*kwargs : dict
        Keywords to be passed along.

    Returns
    -------
    fnames : list
        File names constructed from inputs.
    '''

    if data_type == 'science':
        fnames = construct_science_file_names(*args, **kwargs)
    elif 'selections' in data_type:
        fnames = construct_selections_file_names(data_type, **kwargs)

    return fnames


def construct_selections_file_names(data_type, tstart='*', gls_type=None):
    '''
    Construct a SITL selections file name compliant with
    MMS file name format guidelines.

    MMS SITL selection file names follow the convention
        data_type_[gls_type]_tstart.sav

    Parameters
    ----------
        data_type : str, list, tuple
            Type of selections. Options are abs_selections
            sitl_selections, or gls_selections.
        tstart : str, list
            Start time of data file. The format is
            YYYY-MM-DD-hh-mm-ss. If not given, the default is "*".
        gls_type : str, list
            Type of ground-loop selections. Possible values are:
            mp-dl-unh.

    Returns
    -------
        fnames : list
            File names constructed from inputs.
    '''

    # Convert inputs to iterable lists
    if isinstance(data_type, str):
        data_type = [data_type]
    if isinstance(gls_type, str):
        gls_type = [gls_type]
    if isinstance(tstart, str):
        tstart = [tstart]

    # Accept tuples, as those returned by Construct_Filename
    if isinstance(data_type, tuple):
        data_type = [file[0] for file in data_type]
        tstart = [file[-1] for file in data_type]

        if len(data_type > 2):
            gls_type = [file[1] for file in data_type]
        else:
            gls_type = None

    # Create the file names
    if gls_type is None:
        fnames = ['_'.join((d, g, t+'.sav'))
                  for d in data_type
                  for t in tstart
                  ]

    else:
        fnames = ['_'.join((d, g, t+'.sav'))
                  for d in data_type
                  for g in gls_type
                  for t in tstart
                  ]

    return fnames


def construct_science_file_names(sc, instr=None, mode=None, level=None,
                                 tstart='*', version='*', optdesc=None):
    '''
    Construct a science file name compliant with MMS
    file name format guidelines.

    MMS science file names follow the convention
        sc_instr_mode_level[_optdesc]_tstart_vX.Y.Z.cdf

    Parameters
    ----------
        sc : str, list, tuple
            Spacecraft ID(s)
        instr : str, list
            Instrument ID(s)
        mode : str, list
            Data rate mode(s). Options include slow, fast, srvy, brst
        level : str, list
            Data level(s). Options include l1a, l1b, l2pre, l2, l3
        tstart : str, list
            Start time of data file. In general, the format is
            YYYYMMDDhhmmss for "brst" mode and YYYYMMDD for "srvy"
            mode (though there are exceptions). If not given, the
            default is "*".
        version : str, list
            File version, formatted as "X.Y.Z", where X, Y, and Z
            are integer version numbers.
        optdesc : str, list
            Optional file name descriptor. If multiple parts,
            they should be separated by hyphens ("-"), not under-
            scores ("_").

    Returns
    -------
        fnames : str, list
            File names constructed from inputs.
    '''

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

    # Accept tuples, as those returned by Construct_Filename
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
        fnames = ['_'.join((s, i, m, l, t, 'v'+v+'.cdf'))
                  for s in sc_ids
                  for i in instr
                  for m in mode
                  for l in level
                  for t in tstart
                  for v in version
                  ]
    else:
        fnames = ['_'.join((s, i, m, l, o, t, 'v'+v+'.cdf'))
                  for s in sc_ids
                  for i in instr
                  for m in mode
                  for l in level
                  for o in optdesc
                  for t in tstart
                  for v in version
                  ]
    return fnames


def construct_path(*args, data_type='science', **kwargs):
    '''
    Construct a directory structure compliant with MMS path guidelines.

    MMS paths follow the convention
        selections: sitl/type_selections_[gls_type_]
        brst: sc/instr/mode/level[/optdesc]/<year>/<month>/<day>
        srvy: sc/instr/mode/level[/optdesc]/<year>/<month>

    Parameters
    ----------
        args : dict
            Arguments to be passed along.
        data_type : str
            Type of file names to construct. Options are:
            science or *_selections. If science, inputs are
            passed to construct_science_file_names. If
            *_selections, inputs are passed to
            construct_selections_file_names.
        kwargs : dict
            Keywords to be passed along.

    Returns
    -------
    paths : list
        Paths constructed from inputs.
    '''

    if data_type == 'science':
        paths = construct_science_path(*args, **kwargs)
    elif 'selections' in data_type:
        paths = construct_selections_path(data_type, **kwargs)
    else:
        raise ValueError('Invalid value for keyword data_type')

    return paths


def construct_selections_path(data_type, tstart='*', gls_type=None,
                              root='', files=False):
    '''
    Construct a directory structure compliant with MMS path
    guidelines for SITL selections.

    MMS SITL selections paths follow the convention
        sitl/[data_type]_selections[_gls_type]/

    Parameters
    ----------
        data_type : str, list, tuple
            Type of selections. Options are abs_selections
            sitl_selections, or gls_selections.
        tstart : str, list
            Start time of data file. The format is
            YYYY-MM-DD-hh-mm-ss. If not given, the default is "*".
        gls_type : str, list
            Type of ground-loop selections. Possible values are:
            mp-dl-unh.
        root : str
            Root of the SDC-like directory structure.
        files : bool
            If True, file names are associated with each path.

    Returns
    -------
    paths : list
        Paths constructed from inputs.
    '''

    # Convert inputs to iterable lists
    if isinstance(data_type, str):
        data_type = [data_type]
    if isinstance(gls_type, str):
        gls_type = [gls_type]
    if isinstance(tstart, str):
        tstart = [tstart]

    # Accept tuples, as those returned by Construct_Filename
    if isinstance(data_type, tuple):
        data_type = [file[0] for file in data_type]
        tstart = [file[-1] for file in data_type]

        if len(data_type > 2):
            gls_type = [file[1] for file in data_type]
        else:
            gls_type = None

    # Paths + Files
    if files:
        if gls_type is None:
            paths = [os.path.join(root, 'sitl', d, '_'.join((d, t+'.sav')))
                     for d in data_type
                     for t in tstart
                     ]
        else:
            paths = [os.path.join(root, 'sitl', d, '_'.join((d, g, t+'.sav')))
                     for d in data_type
                     for g in gls_type
                     for t in tstart
                     ]

    # Paths
    else:
        if gls_type is None:
            paths = [os.path.join(root, 'sitl', d)
                     for d in data_type
                     ]
        else:
            paths = [os.path.join(root, 'sitl', d)
                     for d in data_type
                     ]

    return paths


def construct_science_path(sc, instr=None, mode=None, level=None, tstart='*',
                           optdesc=None, root='', files=False):
    '''
    Construct a directory structure compliant with
    MMS path guidelines for science files.

    MMS science paths follow the convention
        brst: sc/instr/mode/level[/optdesc]/<year>/<month>/<day>
        srvy: sc/instr/mode/level[/optdesc]/<year>/<month>

    Parameters
    ----------
        sc : str, list, tuple
            Spacecraft ID(s)
        instr : str, list
            Instrument ID(s)
        mode : str, list
            Data rate mode(s). Options include slow, fast, srvy, brst
        level : str, list
            Data level(s). Options include l1a, l1b, l2pre, l2, l3
        tstart : str, list
            Start time of data file, formatted as a date: '%Y%m%d'.
            If not given, all dates from 20150901 to today's date are
            used.
        optdesc : str, list
            Optional file name descriptor. If multiple parts,
            they should be separated by hyphens ("-"), not under-
            scores ("_").
        root : str
            Root directory at which the directory structure begins.
        files : bool
            If True, file names will be generated and appended to the
            paths. The file tstart will be "YYYYMMDD*" (i.e. the date
            with an asterisk) and the version number will be "*".

    Returns
    -------
    fnames : str, list
        File names constructed from inputs.
    '''

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

    # Accept tuples, as those returned by construct_filename
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
            paths = [os.path.join(root, s, i, m, l, t[0:4], t[4:6], t[6:8],
                                  '_'.join((s, i, m, l, t+'*', 'v*.cdf'))
                                  )
                     if m == 'brst'
                     else
                     os.path.join(root, s, i, m, l, t[0:4], t[4:6],
                                  '_'.join((s, i, m, l, t+'*', 'v*.cdf'))
                                  )
                     for s in sc_ids
                     for i in instr
                     for m in mode
                     for l in level
                     for t in tstart
                     ]
        else:
            paths = [os.path.join(root, s, i, m, l, o, t[0:4], t[4:6], t[6:8],
                                  '_'.join((s, i, m, l, o, t+'*', 'v*.cdf'))
                                  )
                     if m == 'brst'
                     else
                     os.path.join(root, s, i, m, l, o, t[0:4], t[4:6],
                                  '_'.join((s, i, m, l, o, t+'*', 'v*.cdf'))
                                  )
                     for s in sc_ids
                     for i in instr
                     for m in mode
                     for l in level
                     for o in optdesc
                     for t in tstart
                     ]

    # Paths
    else:
        if optdesc is None:
            paths = [os.path.join(root, s, i, m, l, t[0:4], t[4:6], t[6:8])
                     if m == 'brst' else
                     os.path.join(root, s, i, m, l, t[0:4], t[4:6])
                     for s in sc_ids
                     for i in instr
                     for m in mode
                     for l in level
                     for t in tstart
                     ]
        else:
            paths = [os.path.join(root, s, i, m, l, o, t[0:4], t[4:6], t[6:8])
                     if m == 'brst' else
                     os.path.join(root, s, i, m, l, o, t[0:4], t[4:6])
                     for s in sc_ids
                     for i in instr
                     for m in mode
                     for l in level
                     for o in optdesc
                     for t in tstart
                     ]

    return paths


def file_start_time(file_name):
    '''
    Extract the start time from a file name.

    Parameters
    ----------
        file_name : str
            File name from which the start time is extracted.

    Returns
    -------
        fstart : `datetime.datetime`
            Start time of the file, extracted from the file name
    '''

    try:
        # Selections: YYYY-MM-DD-hh-mm-ss
        fstart = re.search('[0-9]{4}(-[0-9]{2}){5}', file_name).group(0)
        fstart = dt.datetime.strptime(fstart, '%Y-%m-%d-%H-%M-%S')
    except AttributeError:
        try:
            # Brst: YYYYMMDDhhmmss
            fstart = re.search('20[0-9]{2}'           # Year
                               '(0[0-9]|1[0-2])'      # Month
                               '([0-2][0-9]|3[0-1])'  # Day
                               '([0-1][0-9]|2[0-4])'  # Hour
                               '[0-5][0-9]'           # Minute
                               '([0-5][0-9]|60)',     # Second
                               file_name).group(0)
            fstart = dt.datetime.strptime(fstart, '%Y%m%d%H%M%S')
        except AttributeError:
            try:
                # Srvy: YYYYMMDD
                fstart = re.search('20[0-9]{2}'            # Year
                                   '(0[0-9]|1[0-2])'       # Month
                                   '([0-2][0-9]|3[0-1])',  # Day
                                   file_name).group(0)
                fstart = dt.datetime.strptime(fstart, '%Y%m%d')
            except AttributeError:
                raise AttributeError('File start time not identified in: \n'
                                     '  "{}"'.format(file_name))

    return fstart


def filename2path(fname, root=''):
    """
    Convert an MMS file name to an MMS path.

    MMS paths take the form

        sc/instr/mode/level[/optdesc]/YYYY/MM[/DD/]

    where the optional descriptor [/optdesc] is included if it is also in the
    file name and day directory [/DD] is included if mode='brst'.

    Parameters
    ----------
    fname : str
        File name to be turned into a path.
    root : str
        Absolute directory

    Returns
    -------
    path : list
        Path to the data file.
    """

    parts = parse_filename(fname)

    # data_type = '*_selections'
    if 'selections' in parts[0]:
        path = os.path.join(root, parts[0])

    # data_type = 'science'
    else:
        # Create the directory structure
        #   sc/instr/mode/level[/optdesc]/YYYY/MM/
        path = os.path.join(root, *part[0:5], part[5][0:4], part[5][4:6])

        # Burst files require the DAY directory
        #   sc/instr/mode/level[/optdesc]/YYYY/MM/DD/
        if part[3] == 'brst':
            path = os.path.join(path, part[5][6:8])

    path = os.path.join(path, fname)

    return path


def filter_time(fnames, start_date, end_date):
    """
    Filter files by their start times.

    Parameters
    ----------
    fnames : str, list
        File names to be filtered.
    start_date : str
        Start date of time interval, formatted as '%Y-%m-%dT%H:%M:%S'
    end_date : str
        End date of time interval, formatted as '%Y-%m-%dT%H:%M:%S'

    Returns
    -------
    paths : list
        Path to the data file.
    """

    # Make sure file names are iterable. Allocate output array
    files = fnames
    if isinstance(files, str):
        files = [files]

    # If dates are strings, convert them to datetimes
    if isinstance(start_date, str):
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
    if isinstance(end_date, str):
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')

    # Parse the time out of the file name
    fstart = [file_start_time(file) for file in files]

    # Sort the files by start time
    isort = sorted(range(len(fstart)), key=lambda k: fstart[k])
    fstart = [fstart[i] for i in isort]
    files = [files[i] for i in isort]

    # End time
    #   - Any files that start on or before END_DATE can be kept
    idx = [i for i, t in enumerate(fstart) if t <= end_date]
    if len(idx) > 0:
        fstart = [fstart[i] for i in idx]
        files = [files[i] for i in idx]
    else:
        fstart = []
        files = []

    # Start time
    #   - Any file with TSTART <= START_DATE can potentially have data
    #     in our time interval of interest.
    #   - Assume the start time of one file marks the end time of the
    #     previous file.
    #   - With this, we look for the file that begins just prior to START_DATE
    #     and throw away any files that start before it.
    idx = [i for i, t in enumerate(fstart) if t >= start_date]
    if (len(idx) == 0) and \
            (len(fstart) > 0) and \
            (fstart[-1].date() == start_date.date()):
        idx = [len(fstart)-1]

    elif (len(idx) != 0) and \
            ((idx[0] != 0) and (fstart[idx[0]] != start_date)):
        idx.insert(0, idx[0]-1)

    if len(idx) > 0:
        fstart = [fstart[i] for i in idx]
        files = [files[i] for i in idx]
    else:
        fstart = []
        files = []

    return files


def filter_version(files, latest=None, version=None, min_version=None):
    '''
    Filter file names according to their version numbers.

    Parameters
    ----------
    files : str, list
        File names to be turned into paths.
    latest : bool
        If True, the latest version of each file type is
        returned. if `version` and `min_version` are not
        set, this is the default.
    version : str
        Only files with this version are returned.
    min_version : str
        All files with version greater or equal to this
        are returned.

    Returns
    -------
    filtered_files : list
        The files remaining after applying filter conditions.
    '''

    if version is None and min is None:
        latest = True
    if ((version is None) + (min_version is None) + (latest is None)) > 1:
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
                if ((vXYZ[0] > vXYZ_ref[0]) or
                        (vXYZ[0] == vXYZ_ref[0] and
                         vXYZ[1] > vXYZ_ref[1]) or
                        (vXYZ[0] == vXYZ_ref[0] and
                         vXYZ[1] == vXYZ_ref[1] and
                         vXYZ[2] > vXYZ_ref[2])):
                    filtered_files[-1] = files[i]

    # All files with version number greater or equal to MIN_VERSION
    elif min_version is not None:
        vXYZ_min = min_version.split('.')
        for idx, v in enumerate(versions):
            vXYZ = v.split('.')
            if ((vXYZ[0] > vXYZ_min[0]) or
                    (vXYZ[0] == vXYZ_min[0] and
                     vXYZ[1] > vXYZ_min[1]) or
                    (vXYZ[0] == vXYZ_min[0] and
                     vXYZ[1] == vXYZ_min[1] and
                     vXYZ[2] >= vXYZ_min[2])):
                filtered_files.append(files[idx])

    # All files with a particular version number
    elif version is not None:
        vXYZ_ref = min_version.split('.')
        for idx, v in enumerate(versions):
            vXYZ = v.split('.')
            if (vXYZ[0] == vXYZ_ref[0] and
                    vXYZ[1] == vXYZ_ref[1] and
                    vXYZ[2] == vXYZ_ref[2]):
                filtered_files.append(files[idx])

    return filtered_files


def load_science_files(sc, instr, mode, level, start_date, end_date,
                       optdesc=None, offline=False, ignore=None,
                       include=None, index_key='Epoch'):
    """
    Download and read data from science data files. Data files that are
    present locally will not be downloaded again.

    Parameters
    ----------
    sc : str, list
        Spacecraft ID.
    instr : str, list
        Instrument ID.
    mode : str, list
        Data rate mode.
    level : str, list
        Data product quality level. Setting level to None, "l2", or "l3"
        automatically sets site to "public".
    end_date : str, `datetime.datetime`
        End time of data interval of interest. If a string, it must be in
        ISO-8601 format: YYYY-MM-DDThh:mm:ss, and is subsequently
        converted to a datetime object.
    ignore : list, optional
        In case a CDF file has columns that are unused / not required,
        then the column names can be passed as a list into the function.
    offline : bool
        If True, file information will be gathered from the local file
        system only (i.e. no requests will be posted to the SDC).
    optdesc : str, list
        Optional descriptor of the data products.
    start_date : str, :class:`datetime.datetime`
        Start time of data interval of interest. If a string, it must be
        in ISO-8601 format: YYYY-MM-DDThh:mm:ss, and is subsequently
        converted to a datetime object.

    Returns
    -------
    data : :class:`pandas.Dataframe`, list
        A list of dataframes containing data from the requested files.
        If only a single file type is request, a single dataframe is
        returned.
    """

    def processing_func(cdf, **kwargs):
        return util.cdf2df(cdf, **kwargs)

    # Download files and sort them into types
    sdc = MMSDownloader(sc, instr, mode, level, optdesc=optdesc,
                        start_date=start_date, end_date=end_date,
                        offline=offline)
    fnames = sdc.download_files()
    fgroups = sort_files(fnames)

    # Load each file type
    data = []
    for fgroup in fgroups:
        dgroup = []
        for file in fgroup:
            df = util._load_raw_file(pathlib.Path(file), processing_func,
                                     ignore=ignore,
                                     include=include,
                                     index_key=index_key
                                     )
            if df is not None:
                dgroup.append(df)
        # Filter to the correct time range
        #   - Will also concatenate dataframes together
        dgroup = util.timefilter(dgroup, start_date, end_date)
        dgroup = dgroup.sort_index()
        data.append(dgroup)

    # Return a single data frame if only one
    # file type is present
    if len(data) == 1:
        data = data[0]

    return data


def _response_text_to_dict(text):
    # Read first line as dict keys. Cut text from TAI keys
    f = io.StringIO(text)
    reader = csv.reader(f, delimiter=',')

    # Read remaining lines into columns
    data = {key: [] for key in next(reader)}
    keys = data.keys()
    for row in reader:
        for item in zip(keys, row):
            data[item[0]].append(item[1])

    return data


def mission_events(start_date=None, end_date=None,
                   start_orbit=None, end_orbit=None,
                   sc=None,
                   source=None, event_type=None):
    """
    Download MMS mission events. See the filters on the webpage
    for more ideas.
        https://lasp.colorado.edu/mms/sdc/public/about/events/#/

    NOTE: some sources, such as 'burst_segment', return a format
          that is not yet parsed properly.

    Parameters
    ----------
    start_date : `datetime`
        Start date of time interval for which information is desired.
    end_date : `datetime`
        End date of time interval for which information is desired.
    start_orbit : `datetime`
        Start date of data interval for which information is desired.
        If provided with start_date, the two must overlap for any data
        to be returned.
    end_orbit : `datetime`
        End orbit of data interval for which information is desired.
        If provided with end_date, the two must overlap for any data
        to be returned.
    sc : str
        Spacecraft ID (mms, mms1, mms2, mms3, mms4) for which event
        information is to be returned.
    source : str
        Source of the mission event. Options include
        'Timeline', 'Burst', 'BDM', 'SITL'
    event_type : str
        Type of mission event. Options include
        BDM: sitl_window, evaluate_metadata, science_roi

    Returns
    -------
    data : dict
        Information about each event.
            ===              ===========
            Key              Description
            ===              ===========
            start_time_utc   Start time of event %Y-%m-%dT%H:%M:%S.%f
            end_time_utc     End time of event %Y-%m-%dT%H:%M:%S.%f
            event_type       Type of event
            sc_id            Spacecraft to which the event applies
            source           Source of event
            description      Description of event
            discussion
            start_orbit      Orbit on which the event started
            end_orbit        Orbit on which the event ended
            tag
            id
            tstart           Start time of event as datetime
            tend             end time of event as datetime
            ===              ===========
    """
    url = 'https://lasp.colorado.edu/' \
          'mms/sdc/public/service/latis/mms_events_view.csv'

    query = {}
    if start_date is not None:
        query['start_time_utc>'] = start_date.strftime('%Y-%m-%d')
    if end_date is not None:
        query['end_time_utc<'] = end_date.strftime('%Y-%m-%d')

    if start_orbit is not None:
        query['start_orbit>'] = start_orbit
    if end_orbit is not None:
        query['end_orbit<'] = end_orbit

    if sc is not None:
        query['sc_id'] = sc
    if source is not None:
        query['source'] = source
    if event_type is not None:
        query['event_type'] = event_type

    resp = requests.get(url, params=query)
    data = _response_text_to_dict(resp.text)

    # Convert to useful types
    types = ['str', 'str', 'str', 'str', 'str', 'str', 'str',
             'int32', 'int32', 'str', 'int32']
    for items in zip(data, types):
        if items[1] == 'str':
            pass
        else:
            data[items[0]] = np.asarray(data[items[0]], dtype=items[1])

    # Add useful tags
    #   - Number of seconds elapsed
    #   - TAISTARTIME as datetime
    #   - TAIENDTIME as datetime
    data["start_time_utc"] = data.pop("start_time_utc "
                                      "(yyyy-MM-dd'T'HH:mm:ss.SSS)"
                                      )
    data["end_time_utc"] = data.pop("end_time_utc "
                                    "(yyyy-MM-dd'T'HH:mm:ss.SSS)"
                                    )

    # NOTE! If data['TAISTARTTIME'] is a scalar, this will not work
    #       unless everything after "in" is turned into a list
    data['tstart'] = [dt.datetime.strptime(
                          value, '%Y-%m-%dT%H:%M:%S.%f'
                          )
                      for value in data['start_time_utc']
                      ]
    data['tend'] = [dt.datetime.strptime(
                        value, '%Y-%m-%dT%H:%M:%S.%f'
                        )
                    for value in data['end_time_utc']
                    ]

    return data


def parse_file_name(fname):
    """
    Parse a file name compliant with MMS file name format guidelines.

    Parameters
    ----------
    fname : str
        File name to be parsed.

    Returns
    -------
    parts : tuple
        The tuple elements are:
            * [0]: Spacecraft IDs
            * [1]: Instrument IDs
            * [2]: Data rate modes
            * [3]: Data levels
            * [4]: Optional descriptor (empty string if not present)
            * [5]: Start times
            * [6]: File version number
    """

    parts = os.path.basename(fname).split('_')

    # data_type = '*_selections'
    if 'selections' in fname:
        # datatype_glstype_YYYY-mm-dd-HH-MM-SS.sav
        if len(parts) == 3:
            gls_type = ''
        else:
            gls_type = parts[2]

        # (data_type, [gls_type,] start_date)
        out = ('_'.join(parts[0:2]), gls_type, parts[-1][0:-4])

    # data_type = 'science'
    else:
        # sc_instr_mode_level_[optdesc]_fstart_vVersion.cdf
        if len(parts) == 6:
            optdesc = ''
        else:
            optdesc = parts[4]

        # (sc, instr, mode, level, [optdesc,] start_date, version)
        out = (*parts[0:4], optdesc, parts[-2], parts[-1][1:-4])

    return out


def parse_time(times):
    """
    Parse the start time of MMS file names.

    Parameters
    ----------
    times : str, list
        Start times of file names.

    Returns
    -------
    parts : list
        A list of tuples. The tuple elements are:
            [0]: Year
            [1]: Month
            [2]: Day
            [3]: Hour
            [4]: Minute
            [5]: Second
    """

    if isinstance(times, str):
        times = [times]

    # Three types:
    #    srvy        YYYYMMDD
    #    brst        YYYYMMDDhhmmss
    #    selections  YYYY-MM-DD-hh-mm-ss
    parts = [None]*len(times)
    for idx, time in enumerate(times):
        if len(time) == 21:
            parts[idx] = (time[0:4], time[5:7], time[8:10],
                          time[11:13], time[14:16], time[17:]
                          )
        elif len(time) == 16:
            parts[idx] = (time[0:4], time[4:6], time[6:8],
                          time[8:10], time[10:12], time[12:14]
                          )
        else:
            parts[idx] = (time[0:4], time[4:6], time[6:8], '00', '00', '00')

    return parts


def read_eva_fom_structure(sav_filename):
    '''
    Returns a dictionary that mirrors the SITL selections fomstr structure
    that is in the IDL .sav file.

    Parameters
    ----------
    sav_filename : str
        Name of the IDL sav file containing the SITL selections

    Returns
    -------
    data : dict
        The FOM structure.
    '''
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sav = scipy.io.readsav(sav_filename)

    assert 'fomstr' in sav, 'save file does not have a fomstr structure'
    fomstr = sav['fomstr']

    d = {'valid': int(fomstr.valid[0]),
         'error': fomstr.error[0],
         'algversion': fomstr.algversion[0],
         'sourceid': fomstr.sourceid[0].tolist(),
         'cyclestart': int(fomstr.cyclestart[0]),
         'numcycles': int(fomstr.numcycles[0]),
         'nsegs': int(fomstr.nsegs[0]),
         'start': [int(x) for x in fomstr.start[0].tolist()],
         'stop': [int(x) for x in fomstr.stop[0].tolist()],
         'seglengths': [int(x) for x in fomstr.seglengths[0].tolist()],
         'fom': [float(x) for x in fomstr.fom[0].tolist()],
         'nbuffs': int(fomstr.nbuffs[0]),
         'mdq': [float(x) for x in fomstr.mdq[0].tolist()],
         'timestamps': [int(x) for x in fomstr.timestamps[0].tolist()],
         'targetbuffs': int(fomstr.targetbuffs[0]),
         'fomave': float(fomstr.fomave[0]),
         'targetratio': float(fomstr.targetratio[0]),
         'minsegmentsize': float(fomstr.minsegmentsize[0]),
         'maxsegmentsize': float(fomstr.maxsegmentsize[0]),
         'pad': int(fomstr.pad[0]),
         'searchratio': float(fomstr.searchratio[0]),
         'fomwindowsize': int(fomstr.fomwindowsize[0]),
         'fomslope': float(fomstr.fomslope[0]),
         'fomskew': float(fomstr.fomskew[0]),
         'fombias': float(fomstr.fombias[0]),
         'metadatainfo': fomstr.metadatainfo[0],
         'oldestavailableburstdata': fomstr.oldestavailableburstdata[0],
         'metadataevaltime': fomstr.metadataevaltime[0]}
    if 'DISCUSSION' in fomstr.dtype.names:
        d['discussion'] = [x for x in fomstr.discussion[0].tolist()]
    if 'NOTE' in fomstr.dtype.names:
        d['note'] = fomstr.note[0]

    # Convert TAI to datetime
    #   - timestaps are TAI seconds elapsed since 1958-01-01
    #   - tt2000 are nanoseconds elapsed since 2000-01-01
    t_1958 = epochs.CDFepoch.compute_tt2000([1958, 1, 1, 0, 0, 0, 0, 0, 0])
    tepoch = epochs.CDFepoch()
    d['datetimestamps'] = tepoch.to_datetime(
                              np.asarray(d['timestamps']) * int(1e9) +
                              t_1958
                              )

    # FOM structure (copy procedure from IDL/SPEDAS/EVA)
    #   - eva_sitl_load_soca_simple
    #   - eva_sitl_strct_read
    #   - mms_convert_from_tai2unix
    #   - mms_tai2unix
    if 'fomslope' in d:
        if d['stop'][d['nsegs']-1] >= d['numcycles']:
            raise ValueError('Number of segments should be <= # cycles.')

        tstart = []
        tstop = []
        t_fom = [d['datetimestamps'][0]]
        fom = [0]
        dt_last = d['datetimestamps'][d['numcycles']-1] - \
                      d['datetimestamps'][d['numcycles']-2]

        # Extract the start and stop times of the FOM values
        # Create a time series for FOM values
        for idx in range(d['nsegs']):
            tstart.append(d['datetimestamps'][d['start'][idx]])
            if d['stop'][idx] <= d['numcycles']-1:
                tstop.append(d['datetimestamps'][d['stop'][idx]+1])
            else:
                tstop.append(d['datetimestamps'][d['numcycles']-1] + dt_last)

            t_fom.extend([tstart[idx], tstart[idx], tstop[idx], tstop[idx]])
            fom.extend([0, d['fom'][idx], d['fom'][idx], 0])

        # Append the last time stamp to the time series
        t_fom.append(d['datetimestamps'][d['numcycles']-1] + dt_last)
        fom.append(0)

    # BAK structure
    else:
        raise NotImplemented('BAK structure has not been implemented')
        nsegs = len(d['fom'])  # BAK

    # Add to output structure
    d['fom_tstart'] = tstart
    d['fom_tstop'] = tstop
    d['t_fom'] = t_fom
    d['y_fom'] = fom

    return d


def read_gls_csv(file_names):
    """
    Read a ground loop selections (gls) CSV file or files.

    Parameters
    ----------
    file_names : str, list
        Name of the CSV file(s) to be read

    Returns
    -------
    data : dict
        Data contained in the CSV file
    """
    if isinstance(file_names, str):
        file_names = [file_names]
    
    keys = ['start_time', 'end_time', 'fom', 'discussion',
            'fom_tstart', 'fom_tstop', 't_fom', 'y_fom']
    tset = set()
    nold = 0
    data = {key: [] for key in keys}
    for file in file_names:
        with open(file) as f:
            reader = csv.reader(f)
            for row in reader:
                tstart = dt.datetime.strptime(
                             row[0], '%Y-%m-%d %H:%M:%S'
                             )
                tend = dt.datetime.strptime(
                           row[1], '%Y-%m-%d %H:%M:%S'
                           )
                
                # Keep only unique elements
                tset.add(tstart)
                nnew = len(tset)
                if nnew == nold:
                    continue
                else:
                    nold = nnew

                data['start_time'].append(row[0])
                data['end_time'].append(row[1])
                data['fom'].append(row[2])
                data['discussion'].append(','.join(row[3:]))
                data['fom_tstart'].append(tstart)
                data['fom_tstop'].append(tend)
                data['t_fom'].extend([tstart, tstart, tend, tend])
                data['y_fom'].extend([0, row[2], row[2], 0])

    # Change data types
    data['fom'] = np.array(data.pop('fom'), dtype='float32')
    data['y_fom'] = np.array(data.pop('y_fom'), dtype='float32')

    return data


def _sdc_parse_form(r):
    '''Parse key-value pairs from the log-in form

    Parameters
    ----------
    r (object):    requests.response object.

    Returns
    -------
    form (dict):   key-value pairs parsed from the form.
    '''
    # Find action URL
    pstart = r.text.find('<form')
    pend = r.text.find('>', pstart)
    paction = r.text.find('action', pstart, pend)
    pquote1 = r.text.find('"', pstart, pend)
    pquote2 = r.text.find('"', pquote1+1, pend)
    url5 = r.text[pquote1+1:pquote2]
    url5 = url5.replace('&#x3a;', ':')
    url5 = url5.replace('&#x2f;', '/')

    # Parse values from the form
    pinput = r.text.find('<input', pend+1)
    inputs = {}
    while pinput != -1:
        # Parse the name-value pair
        pend = r.text.find('/>', pinput)

        # Name
        pname = r.text.find('name', pinput, pend)
        pquote1 = r.text.find('"', pname, pend)
        pquote2 = r.text.find('"', pquote1+1, pend)
        name = r.text[pquote1+1:pquote2]

        # Value
        if pname != -1:
            pvalue = r.text.find('value', pquote2+1, pend)
            pquote1 = r.text.find('"', pvalue, pend)
            pquote2 = r.text.find('"', pquote1+1, pend)
            value = r.text[pquote1+1:pquote2]
            value = value.replace('&#x3a;', ':')

            # Extract the values
            inputs[name] = value

        # Next iteraction
        pinput = r.text.find('<input', pend+1)

    form = {'url': url5,
            'payload': inputs}

    return form


def sdc_login(username=None, password=None):
    '''
    Log-In to the MMS Science Data Center.

    Parameters
    -----------
    username : str
        Account username.
    password : str
        Account password.

    Returns
    --------
    Cookies : dict
        Session cookies for continued access to the SDC. Can
        be passed to an instance of requests.Session.
    '''

    # Use login credentials from heliopyrc
    if username is None:
        username = sdc_username
    if password is None:
        password = sdc_password

    # Disable warnings because we are not going to obtain certificates
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Attempt to access the site
    #   - Each of the redirects are stored in the history attribute
    url0 = 'https://lasp.colorado.edu/mms/sdc/team/'
    r = requests.get(url0, verify=False)

    # Extract cookies and url
    cookies = r.cookies
    for response in r.history:
        cookies.update(response.cookies)

        try:
            url = response.headers['Location']
        except:
            pass

    # Submit login information
    payload = {'j_username': username, 'j_password': password}
    r = requests.post(url, cookies=cookies, data=payload, verify=False)

    # After submitting info, we land on a page with a form
    #   - Parse form and submit values to continue
    form = _sdc_parse_form(r)
    r = requests.post(form['url'],
                      cookies=cookies,
                      data=form['payload'],
                      verify=False
                      )

    # Update cookies to get session information
    cookies = r.cookies
    for response in r.history:
        cookies.update(response.cookies)

    return cookies


def sitl_selections(data_type='abs_selections', gls_type=None,
                    start_date=None, end_date=None):
    """
    Download SITL selections from the SDC.

    Parameters
    ----------
    data_type : str
        Type of SITL selections to download. Options are
            'abs_selections', 'sitl_selections', 'gls_selections'
    gls_type : str
        Type of gls_selections. Options are
            'mp-dl-unh'
    start_date : `dt.datetime` or str
        Start date of data interval
    end_date : `dt.datetime` or str
        End date of data interval

    Returns
    -------
    local_files : list
        Names of the selection files that were downloaded. Files
        can be read using mms.read_eva_fom_structure()
    """

    if gls_type is not None:
        data_type = '_'.join((data_type, gls_type))

    # Setup the API
    sdc = MMSDownloader()
    sdc.data_type = data_type
    sdc.start_date = start_date
    sdc.end_date = end_date

    # Download the files
    local_files = sdc.download_files()
    return local_files


def sort_files(files):
    """
    Sort MMS file names by data product and time.

    Parameters
    ----------
    files : str, list of str
        Files to be sorted

    Returns
    -------
    sorted : tuple
        Sorted file names. Each tuple element corresponds to
        a unique data product.
    """

    # File types and start times
    parts = [parse_file_name(file) for file in files]
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
    allowed_probes = [str(i + 1) for i in range(4)]
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


def available_files(probe, instrument, starttime, endtime, data_rate='',
                    product_string=''):
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
    if starttime.date() == endtime.date():
        end_date = (endtime.date() + dt.timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        end_date = endtime.strftime('%Y-%m-%d')

    query = {}
    query['sc_id'] = 'mms' + probe
    query['instrument_id'] = instrument
    if len(data_rate):
        query['data_rate_mode'] = data_rate
    if len(product_string):
        query['descriptor'] = product_string
    query['start_date'] = start_date
    query['end_date'] = end_date

    r = requests.get(query_url, params=query)
    files = r.text.split(',')
    files = filter_time(files, starttime, endtime)
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
        files = available_files(probe, instrument, starttime, endtime,
                                data_rate, product_string)
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
                for chunk in tqdm.tqdm(
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
