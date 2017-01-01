from concurrent.futures import ThreadPoolExecutor
import io
import datrie
from requests.models import Response
import string
import threading
import time
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
    from Queue import Queue, Empty
except ImportError:
    from urllib.parse import quote_plus
    from queue import Queue, Empty

from sparc.configuration import container
from sparc.utils import requests

from sparc.logging import logging
logger = logging.getLogger(__name__)

DEFAULT_PAGINATION_LIMIT = '25'
DEFAULT_REQUEST_WORKERS = 1


class MellonUnicodeFileFromURLItemAndConfig(
                        mellon.file.MellonUnicodeFileFromFileStreamAndConfig):
    
    def __init__(self, url, response, config):
        self.url = url 
        super(MellonUnicodeFileFromURLItemAndConfig, self).__init__(
                    io.StringIO(response['body']['storage']['value']), config)
    
    def __str__(self):
        return "unicode file at location {}".format(self.url)
mellonUnicodeFileFromURLItemAndConfigFactory = Factory(
                                MellonUnicodeFileFromURLItemAndConfig)


class MellonByteFileFromConfluenceAttachment(
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
            
    
    def __init__(self, url, config, requester, req_kwargs):
        r = requester.request('GET', url, stream=True, **req_kwargs)
        r.raise_for_status()
        MellonByteFileFromConfluenceAttachment.add_reader(r)
        self.url = url
        super(MellonByteFileFromConfluenceAttachment, self).__init__(r, config)
    
    def __str__(self):
        return "byte file attachment at location {}".format(self.url)
mellonByteFileFromConfluenceAttachmentFactory = Factory(
                                    MellonByteFileFromConfluenceAttachment)


class MellonUnicodeFileFromConfluenceAttachment(
                            mellon.file.MellonUnicodeFileFromFileStreamAndConfig):
    @classmethod
    def replace_line_iterator(cls, response):
        """
        Replace the default __iter__ method on a response object to iterate
        line-by-line as opposed to default byte-based increments.
        """
        response.__iter__ = types.MethodType(Response.iter_lines, response)

    def __init__(self, url, config, requester, req_kwargs):
        r = requester.request('GET', url, stream=True, **req_kwargs)
        r.raise_for_status()
        MellonUnicodeFileFromConfluenceAttachment.replace_line_iterator(r)
        self.url = url
        super(MellonUnicodeFileFromConfluenceAttachment, self).__init__(r, config)
    
    def __str__(self):
        return "unicode file attachment at location {}".format(self.url)
mellonUnicodeFileFromConfluenceAttachmentFactory = Factory(
                                    MellonUnicodeFileFromConfluenceAttachment)

@interface.implementer(IMellonFileProvider)
class TSMellonFileProviderFromConfluenceConfig(object):
    
    
    def debug(self):
        logger.setLevel('DEBUG')
    
    def __init__(self, config):
        #General items
        self.config = config
        self.requester = self.get_requester()
        
        # Concurrency properties
        self.mellon_files = Queue() # TS queue for IMellonFile providers
        self.jobs = Queue() # TS queue for async jobs (concurrent.futures.Future objects)
        self.count = 0 #keep track of job numbers for debuging
        self.job_id = 0 #assign and track unique job ids
        
        # API properties
        max_workers= int(container.IPyContainerConfigValue\
                            (config['ConfluenceSpaceContent']).
                                get('RequestWorkers', DEFAULT_REQUEST_WORKERS))
        self.api_executer = ThreadPoolExecutor(max_workers = max_workers)
        self.api_session = FuturesSession(self.api_executer)
        
        self.api_base = \
            self.config['ConfluenceSpaceContent']['ConfluenceConnection']['url']
        self.api_limit = '&limit=' + str(container.IPyContainerConfigValue\
                                (config['ConfluenceSpaceContent']).\
                                    get('ContentPaginationLimit', 
                                        DEFAULT_PAGINATION_LIMIT))
        self.api_expand = '&expand=history,version,body.storage'
        
        # Content directives
        self.prune = datrie.Trie(string.printable) #make sure to not request same data twice from Confluence API
        self.content_get_history = \
            container.IPyContainerConfigValue(
                config['ConfluenceSpaceContent']).get('SearchHistory', False)
        
        logger.debug(u"Threaded Confluence Mellon file provider initialized with {} worker threads".format(max_workers))
    
    def add_job(self, job):
        self.count += 1
        self.job_id += 1
        self.jobs.put((self.job_id, job, ))
        logger.debug('Job queue count at {}'.format(self.count))
    
    def get_job(self):
        job_id, job = self.jobs.get_nowait()
        self.count -= 1
        logger.debug('Job queue count at {}'.format(self.count))
        return (job_id, job, )

    def get_requester(self):
        """Retrieve the sparc.utils.requests.IRequest based on resolution and configuration
        """
        req = None
        if 'RequestOptions' in self.config['ConfluenceSpaceContent']:
            req = requests.IRequest(self.config['ConfluenceSpaceContent'])
        sm = component.getSiteManager()
        self.requester = sm.getUtility(requests.IRequestResolver)(request=req)
        self.requester.req_kwargs = self.req_kwargs
        return self.requester
    
    @property
    def api_filter(self):
        """CQL based content filter.  Can be specified in config, or defaults to
        all content.
        """
        if 'ContentSearch' in self.config['ConfluenceSpaceContent']:
            return '/search?cql=' + quote_plus(\
                        self.config['ConfluenceSpaceContent']['ContentSearch'])
        return "/search?cql=" + \
                    quote_plus("type IN (page, blogpost, comment, attachment)")
    
    
    @property
    def req_kwargs(self):
        """Dict of kwargs to be passed into Requests API"""
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
        

    def get_mellon_file(self, item):
        """Return a new IMellonFile provider based on a Confluence JSON content item
        
        Args:
            item: Dict JSON Confluence content item
        """
        if item['type'] == 'attachment':
            bin_checker = component.createObject(u"mellon.factories.confluence.attachment_bin_checker", item)
            if bin_checker.check():
                logger.debug('creating mellon byte file for attachment content {} with link {}'.format(item['id'], item['_links']['download']))
                return MellonByteFileFromConfluenceAttachment(
                    self.api_base + item['_links']['download'], self.config, 
                    self.requester, self.req_kwargs)
            else:
                logger.debug('creating mellon unicode file for attachment content {} with link {}'.format(item['id'], item['_links']['download']))
                return MellonUnicodeFileFromConfluenceAttachment(
                    self.api_base + item['_links']['download'], self.config, 
                    self.requester, self.req_kwargs)
                
        else:
            return MellonUnicodeFileFromURLItemAndConfig(
                    self.api_base + item['_links']['webui'], item, self.config)

    def get_item_history_info(self, item):
        """Generator of historical version urls for given content item
        
        note:  urls are not guaranteed to be valid
        
        Return: (version, historical_url, )
        """
        version = int(item['version']['number']) - 1
        while version:
            yield (version, self.api_base + '/rest/api/content/' + item['id'] + \
                        '?status=historical&version=' + \
                        str(version) + self.api_expand)
            version -= 1
    
    def process_item(self, item):
        identifier = item['id'] + '---' + str(item['version']['number'])
        if identifier not in self.prune:
            logger.debug('adding job to create mellon file for content item {} at version {}'.format(item['id'], item['version']['number']))
            self.add_job(self.api_executer.submit(self.get_mellon_file, item))
            if item['history'].get('latest', False) and self.content_get_history: # add jobs for historical item versions if configured
                for version, historical_url in self.get_item_history_info(item):
                    logger.debug('adding job to get historical version {} for item {}'.format(version, item['id']))
                    self.add_job(self.api_session.request(
                        'GET',
                        historical_url,
                        **self.req_kwargs))
            self.prune[identifier] = None
        else:
            logger.debug(u"skipping already processed item {} at {}".format(item['id'], self.api_base+item['_links']['webui']))
            
        
    
    def process_results(self, result):
        if 'results' in result:
            logger.info(u"processing {} results from Confluence API response".format(len(result['results'])))
            for item in result['results']:
                self.process_item(item)
            if 'next' in result['_links']: # add next results pagination into job queue
                logger.debug('adding job to retrieve next results pagination at {}'.format(result['_links']['next']))
                self.add_job(self.api_session.request(
                            'GET',
                            result['_links']['base'] + result['_links']['next'],
                            **self.req_kwargs))
 
    def generate_mellon_files(self):
        """Threaded generator of IMellonFile providers populated to mellon_file queue"""
        # init API entry point
        r = {'_links': {'base': self.api_base, 
                        'next': '/rest/api/content'+self.api_filter + \
                                self.api_limit + self.api_expand}}
        self.debug()
        with warnings.catch_warnings():
            if self.requester.gooble_warnings:
                # TODO: limit this to only requests-related warnings
                warnings.simplefilter("ignore")
            #initialize async job queue with initial API call
            logger.debug('adding job to retreive initial results pagination at {}'.format(r['_links']['next']))
            self.add_job(self.api_session.request(
                                    'GET',
                                    r['_links']['base'] + r['_links']['next'],
                                    **self.req_kwargs))
            #continuously monitor job queue until it is empty.  Job results will be:
            # - JSON API results based item feed from CQL query 
            # - JSON API historical item version from content query
            # - IMellonFile provider
            while not self.jobs.empty():
                job_id, job = self.get_job()
                logger.debug('blocking while waiting for queued job {} to complete'.format(job_id))
                result = job.result()
                
                if mellon.IMellonFile.providedBy(result):
                    logger.debug('publishing mellon file to asynchronous iteration queue {}'.format(result))
                    self.mellon_files.put(result)
                    continue
                
                result.raise_for_status()
                content = result.json()
                
                if 'results' in content:
                    self.process_results(content)
                else:
                    self.process_item(content)

    
    def __iter__(self):
        """Threaded generator of IMellonFile providers
        """
        t = threading.Thread(target=self.generate_mellon_files)
        t.daemon = True
        t.start()
        while t.is_alive() or not self.mellon_files.empty():
            try:
                while not self.mellon_files.empty():
                    yield self.mellon_files.get_nowait()
            except Empty:
                pass
            time.sleep(.5)
        t.join()
        logger.debug('exiting asynchronous iteration queue publisher thread')

tsMellonFileProviderFromConfluenceConfigFactory = Factory(TSMellonFileProviderFromConfluenceConfig)
interface.alsoProvides(tsMellonFileProviderFromConfluenceConfigFactory, IMellonFileProviderFactory)
