import io
import datrie
import string
import types
import warnings
from requests_futures.sessions import FuturesSession
from zope import component
from zope import interface
from zope.component.factory import Factory
from mellon import IMellonFileProvider
from mellon import IMellonFileProviderFactory
import mellon.file

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus

from sparc.utils import requests

from sparc.logging import logging
logger = logging.getLogger(__name__)

PAGINATION_LIMIT = '25'
DEFAULT_REQUEST_WORKERS = 2


class MellonByteFileFromURLConfigAndRequester(
                            mellon.file.MellonByteFileFromFileStreamAndConfig):
    
    @classmethod
    def add_reader(cls, response):
        """
        Add a read() method to a Requests Response object that will make calls
        to Response.iter_content().  Allows usage with Mellon file base classes
        that expect Python file-like streamability via the read() call
        """
        def _reader(self, size=0):
            buffer = self.raw.read(size)
            if len(buffer):
                logger.debug(u"read {} bytes from streamed url byte file {}".format(len(buffer), self))
            return buffer
        response.read = types.MethodType(_reader, response)
            
    
    def __init__(self, url, config, requester, kwargs):
        r = requester.request('GET', url, stream=True, **kwargs)
        r.raise_for_status()
        MellonByteFileFromURLConfigAndRequester.add_reader(r)
        self.url = url
        super(MellonByteFileFromURLConfigAndRequester, self).__init__(r, config)
    
    def __str__(self):
        return "byte file at location {}".format(self.url)
mellonByteFileFromRURLConfigAndRequesterFactory = Factory(
                                    MellonByteFileFromURLConfigAndRequester)

class MellonUnicodeFileFromBaseURLResponseAndConfig(
                        mellon.file.MellonUnicodeFileFromFileStreamAndConfig):
    
    def __init__(self, url, response, config):
        self.url = url 
        super(MellonUnicodeFileFromBaseURLResponseAndConfig, self).__init__(
                    io.StringIO(response['body']['storage']['value']), config)
    
    def __str__(self):
        return "unicode file at location {}".format(self.url)
mellonUnicodeFileFromResponseAndConfigFactory = Factory(
                                MellonUnicodeFileFromBaseURLResponseAndConfig)

@interface.implementer(IMellonFileProvider)
class MellonFileProviderFromConfluenceConfig(object):
    
    def __init__(self, config):
        """Init
        
        Args:
            config: sparc.configuration.container.ISparcAppPyContainerConfiguration
                    provider with:
                      - mellon[config_definitions.yaml:MellonSnippet] entry
                      - mellon.factories.confluence[configure.yaml:ConfluenceSpaceContent] entry
        """
        self.config = config
        self.prune = datrie.Trie(string.printable) #make sure to not request same data twice from Confluence API
        self.url = self.config\
                ['ConfluenceSpaceContent']['ConfluenceConnection']['url'] + \
                                                            '/rest/api/content'
        #We'll leverage async io for item history calls to speed thrings up (see https://github.com/ross/requests-futures)
        self.async_session = FuturesSession(
                        max_workers=int(config['ConfluenceSpaceContent'].get(
                                    'RequestWorkers', DEFAULT_REQUEST_WORKERS)))
        
        # get a requester (used for non-async io API calls)
        req = None
        if 'RequestOptions' in config['ConfluenceSpaceContent']:
            req = requests.IRequest(config['ConfluenceSpaceContent'])
        sm = component.getSiteManager()
        self.requester = sm.getUtility(requests.IRequestResolver)(request=req)
        self.requester.req_kwargs = self._kwargs
        logger.debug(u"initialized Confluence Mellon File factory with starting URL {}".format(self._start_url))

    @property
    def _expand(self):
        """API content expansions (insures JSON dict key availability)"""
        return '&expand=history,version,body.storage'
    
    @property
    def _filter(self):
        """CQL based content filter.  Can be specified in config, or defaults to
        all content.
        """
        if 'ContentSearch' in self.config['ConfluenceSpaceContent']:
            return '/search?cql=' + quote_plus(\
                        self.config['ConfluenceSpaceContent']['ContentSearch'])
        return "/search?cql=" + quote_plus("type IN (page, blogpost, comment, attachment)")

    @property
    def _start_url(self):
        """First API call URL (with pagination limit parameter)"""
        _start_url = self.url
        if self._filter:
            _start_url = _start_url + self._filter
        _start_url = _start_url + ('&limit='+PAGINATION_LIMIT if self._filter \
                                                else '?limit='+PAGINATION_LIMIT)
        return _start_url+self._expand

    @property
    def _kwargs(self):
        """Dict of kwargs to be passed into self.requester (e.g. Requests API)"""
        _kwargs = {}
        _conn_params = self.config['ConfluenceSpaceContent']['ConfluenceConnection']
        if _conn_params['username']:
            _kwargs['auth'] = \
                (_conn_params['username'], 
                 _conn_params['password'] if 'password' in _conn_params else '')
        if 'RequestOptions' in self.config['ConfluenceSpaceContent']:
            if 'req_kwargs' in self.config['ConfluenceSpaceContent']['RequestOptions']:
                _kwargs.update(self.config['ConfluenceSpaceContent']['RequestOptions']['req_kwargs'])
        return _kwargs

    def _request(self, url):
        """Perform a HTTP request, check for error, and return JSON response"""
        #import pdb;pdb.set_trace()
        r = self.requester.request('GET', url)
        r.raise_for_status()
        return r.json()
    
    def _get_mfile_from_citem(self, base_url, i):
        """Return a new IMellonFile provider based on a Confluence JSON content item
        
        Args:
            see _process_item()
        """
        if i['type'] == 'attachment':
            return MellonByteFileFromURLConfigAndRequester(
                    base_url+i['_links']['download'], self.config, 
                    self.requester, self._kwargs)
        else:
            return MellonUnicodeFileFromBaseURLResponseAndConfig(
                    base_url+ i['_links']['webui'], i, self.config)

    def _get_item_history(self, base_url, i):
        """Generator of IMellonFile providers for an item's historical versions.
           
        This will respect the self.requester settings (even though calls to 
        the Requests library will happen outside of the self.requester context)
        
        Args:
            see _process_item()
        """  
        session_requests = []
        version = int(i['version']['number']) - 1
        while version:
            ver_url = self.url + '/' + i['id'] + \
                        '?status=historical&version=' + \
                        str(version) + self._expand
            logger.debug(u"queueing Confluence item version {} for item {} for asynchronous processing".format(version, i['id']))
            session_requests.append((self.async_session.request('GET', ver_url, **self._kwargs), version, ))
            version -= 1
        
        for _req, version in session_requests:
            r = _req.result()
            r.raise_for_status()
            i = r.json()
            logger.debug(u"processed Confluence item version {} for item {}".format(version, i['id']))
            yield self._get_mfile_from_citem(base_url, i)

    def _process_versions(self, base_url, i):
        """Generator for IMellonFile provider Confluence API content item and
           its historical versions (if config indicates to retrieve item
           history).
        Args:
            see _process_item()
        """
        # Return IMellonFile for item
        version = int(i['version']['number'])
        logger.debug(u"processing Confluence item version {} for item {}".format(version, i['id']))
        yield self._get_mfile_from_citem(base_url, i)
        
        # recurse through item history (if config indicates to do so)
        # we'll do this with async io because it can take a while to make lots
        # of API calls.
        if self.config['ConfluenceSpaceContent'].get('SearchHistory', False):
            if self.requester.gooble_warnings:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    for f in self._get_item_history(base_url, i):
                        yield f
            else:
                for f in self._get_item_history(base_url, i):
                    yield f
            

    def _process_item(self, base_url, i):
        """Generator of IMellonFile providers related to a Confluence JSON content item
        
        This will keep track of processed items via a trie data-structure for
        memory efficiency.  Content items will only be processed once.  Item 
        history will be returned based on configuration preference.
        
        Args:
            base_url: Unicode base url string, corresponding to a Confluence API
                      JSON return entry for ['_links']['base']
            i: JSON item result entry with the following keys available/expanded:
                - history
                - version
                - body.storage
        """
        if i['id'] not in self.prune:
            logger.debug(u"processing Confluence item at {}".format(base_url+i['_links']['webui']))
            for f in self._process_versions(base_url, i):
                yield f
            self.prune[i['id']] = None
        else:
            logger.debug(u"skipping already processed item at {}".format(base_url+i['_links']['webui']))

    def __iter__(self):
        """
        Iterate content based on a CQL search (which will return 'results').
        If config hasn't specified any criteria, default to all Confluence
        items 
        """
        # we don't do async here because results come back based on pagination settings
        r = {'_links': {'next': self._start_url}}
        while 'next' in r['_links']:
            r = self._request(r['_links']['next'])
            for i in r['results']:
                for f in self._process_item(r['_links']['base'], i): # f is a mellon file of a Confluence item version
                    yield f

            
mellonFileProviderFromConfluenceConfigFactory = Factory(MellonFileProviderFromConfluenceConfig)
interface.alsoProvides(mellonFileProviderFromConfluenceConfigFactory, IMellonFileProviderFactory)