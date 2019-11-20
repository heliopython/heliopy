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
import requests
import tqdm.auto as tqdm
import urllib

import heliopy
from heliopy.data import util
import sunpy.time
import scipy.io

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
                raise ValueError('Invalid value for attribute "' + name + '".')

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
            file = self.fnames()[0]
        except IndexError:
            file = ''

        # Reset the time interval
        self.set_interval(interval_in)

        return file

    def get_interval(self):
        """
        Get the time interval of interest.

        Returns
        ----------
        interval : sunpy.time.TimeRange
            Start and end time of the data interval
        """
        return sunpy.time.TimeRange(self.start_date, self.end_date)

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
            file = self.downloads()[0]
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
        """Obtain file names from the SDC."""

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

    def downloads(self):
        '''
        Download multiple files. First, search the local file system
        to see if any of the files have been downloaded previously.

        Returns
        -------
        local_files : list
            Names of the local files. Remote files downloaded
            only if they do not already exist locally
        '''
        self._info_type = 'download'
        # Build the URL sans query
        url = self.url(query=False)

        # Get available files
        local_files, remote_files = self.search()
        if self.offline:
            return local_files

        # Get information on the files that were found
        #   - To do that, specify the specific files. This sets all other
        #     properties to None
        #   - Save the state of the object as it currently is so that it can
        #     be restored
        #   - Setting FILES will indirectly cause SITE='public'. Keep track
        #     of SITE.
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

            # Downloading and progress bar:
            # https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
            # https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
            try:
                r = self._session.post(url,
                                       data={'file': info['file_name']},
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

            local_files.append(file)

        self.files = None
        for key in state:
            setattr(self, key, state[key])

        return local_files

    def file_info(self):
        '''
        Obtain file information from the SDC.

        Returns
        -------
        file_info : list
            Information about each file.
        '''
        self._info_type = 'file_info'
        response = self.post()
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
        response = self.post()

        return response.text.split(',')

    def get(self):
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
        downloaded_files = self.download_files(remote_files)
        local_files.append(downloaded_files)

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
        response = self.Get()
        return response.json()

def construct_file_names(*args, data_type='science', **kwargs):
    '''
    Construct a file name compliant with MMS file name format guidelines.

    MMS file names follow the convention
        sc_instr_mode_level[_optdesc]_tstart_vX.Y.Z.cdf

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
                raise AttributeError('File start time not identified.')

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
                     (vXYZ[0] == vXYZ_ref[0] and vXYZ[1] > vXYZ_ref[1]) or
                     (vXYZ[0] == vXYZ_ref[0] and
                      vXYZ[1] == vXYZ_ref[1] and
                      vXYZ[2] > vXYZ_ref[2]
                      )
                    ):
                    # Select the last file
                    filtered_files[-1] = files[i]

    # All files with version number greater or equal to MIN_VERSION
    elif min_version is not None:
        vXYZ_min = min_version.split('.')
        for idx, v in enumerate(versions):
            vXYZ = v.split('.')
            if ((vXYZ[0] > vXYZ_min[0]) or
                (vXYZ[0] == vXYZ_min[0] and vXYZ[1] > vXYZ_min[1]) or
                (vXYZ[0] == vXYZ_min[0] and
                 vXYZ[1] == vXYZ_min[1] and
                 vXYZ[2] >= vXYZ_min[2]
                 )
                ):
                # Append the file if it passes the criteria
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
                # Keep the file if it has the right version
                filtered_files.append(files[idx])

    return filtered_files


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
            [0]: Spacecraft IDs
            [1]: Instrument IDs
            [2]: Data rate modes
            [3]: Data levels
            [4]: Optional descriptor (empty string if not present)
            [5]: Start times
            [6]: File version number
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


def read_selections(sav_filename):
    '''
    Returns a dictionary that mirrors the SITL selections fomstr structure
    that is in the IDL .sav file.

    Parameters
    ----------
    sav_filename : str
        Name of the IDL sav file containing the SITL selections

    Returns
    -------
    d : dict
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
    return d


def sitl_selections(data_type='abs_selections', gls_type='',
                    start_date=None, end_date=None):
    """Obtain version information from the SDC."""

    if gls_type is not None:
        data_type = '_'.join((data_type, gls_type))

    # Setup the API
    api = MrMMS_SDC_API()
    api.data_type = data_type
    api.start_date = start_date
    api.end_date = end_date

    # Download the files
    file_names = api.file_names()
    local_files = api.download_files(file_names)

    return local_files


def sort_files(files):
    """
    Sort MMS file names by data product and time.

    Parameters:
    files : str, list
        Files to be sorted

    Returns
    -------
    sorted : tuple
        Sorted file names. Each tuple element corresponds to
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
