from bs4 import BeautifulSoup
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
from mellon import IApplyAuthorizationContext
from mellon import IMellonFileProvider
from mellon import IMellonFileProviderFactory
from mellon import ITextSnippet
import mellon.file
from . import IConfluenceMellonFile
from . import IConfluenceBytesSnippet
from . import IConfluenceUnicodeSnippet

try:
    from urllib import quote_plus
    from Queue import Queue, Empty
except ImportError:
    from urllib.parse import quote_plus
    from queue import Queue, Empty

from sparc.utils import requests

from sparc.logging import logging
logger = logging.getLogger(__name__)

DEFAULT_PAGINATION_LIMIT = '25'
DEFAULT_REQUEST_WORKERS = 1

@interface.implementer(IConfluenceMellonFile)
class MellonUnicodeFileFromURLItemAndConfig(
                        mellon.file.MellonUnicodeFileFromFileStreamAndConfig):
    
    def __init__(self, url, response, config):
        self.url = url 
        self.config = config
        self.strip_html = \
                    self.config.mapping()['ConfluenceSpaceContent'].get(
                                                        'StripHtmlTags', False)
        ifaces = [IConfluenceUnicodeSnippet]
        if self.strip_html:
            ifaces.append(ITextSnippet)
        soup = BeautifulSoup(response['body']['storage']['value'], 'html.parser')
        text = soup.prettify() if not self.strip_html else soup.get_text()
        #logger.debug("initialized new Mellon file from Confluence with content: \n\n{}\n\n".format(text))
        super(MellonUnicodeFileFromURLItemAndConfig, self).__init__(
                    io.StringIO(text), config,
                    snippet_interfaces=ifaces)
    
    def __str__(self):
        return "unicode file at location {}".format(self.url)
    
#    def _process_line(self, line):
#        if not self.strip_html:
#            logger.debug("processing mellon file line: \n\t{}".format(line))
#            return line
#        soup = BeautifulSoup(line, 'html.parser')
#        #logger.debug("processing mellon file line: \n\n\t{}\n\nto plain text:\n\n\t{}\n\n".format(line, soup.get_text()))
#        return soup.get_text()
        
mellonUnicodeFileFromURLItemAndConfigFactory = Factory(
                                MellonUnicodeFileFromURLItemAndConfig)
#interface.classImplements(MellonUnicodeFileFromURLItemAndConfig, IConfluenceMellonFile)

@interface.implementer(IConfluenceMellonFile)
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
        self.config = config
        r = requester.request('GET', url, stream=True, **req_kwargs)
        r.raise_for_status()
        MellonUnicodeFileFromConfluenceAttachment.replace_line_iterator(r)
        self.url = url
        self.strip_html = \
                    self.config.mapping()['ConfluenceSpaceContent'].get(
                                                        'StripHtmlTags', False)
        ifaces = [IConfluenceUnicodeSnippet]
        if self.strip_html:
            ifaces.append(ITextSnippet)
        super(MellonUnicodeFileFromConfluenceAttachment, self).\
                    __init__(r, config, snippet_interfaces=ifaces)
    
    def __str__(self):
        return "unicode file attachment at location {}".format(self.url)
    
    def _process_line(self, line):
        if not self.strip_html:
            #logger.debug("processing mellon file line: \n\t{}".format(line))
            return line
        soup = BeautifulSoup(line, 'html.parser')
        #logger.debug("processing mellon file line: \n\n\t{}\n\nto plain text:\n\n\t{}\n\n".format(line, soup.get_text()))
        return soup.get_text()
mellonUnicodeFileFromConfluenceAttachmentFactory = Factory(
                                    MellonUnicodeFileFromConfluenceAttachment)
#interface.classImplements(MellonUnicodeFileFromConfluenceAttachment, IConfluenceMellonFile)

@interface.implementer(IConfluenceMellonFile)
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
        super(MellonByteFileFromConfluenceAttachment, self).\
                    __init__(r, config, snippet_interfaces=[IConfluenceBytesSnippet])
    
    def __str__(self):
        return "byte file attachment at location {}".format(self.url)
mellonByteFileFromConfluenceAttachmentFactory = Factory(
                                    MellonByteFileFromConfluenceAttachment)
#interface.classImplements(MellonByteFileFromConfluenceAttachment, IConfluenceMellonFile)

@interface.implementer(IMellonFileProvider)
class TSMellonFileProviderFromConfluenceConfig(object):
    
    
    def debug(self):
        logger.setLevel('DEBUG')
    
    def __init__(self, config):
        #General items
        self.config = config
        self.security_context = self.authorization_context()
        self.requester = self.get_requester()
        
        # Concurrency properties
        self.mellon_files = Queue() # TS queue for IMellonFile providers
        self.jobs = Queue() # TS queue for async jobs (concurrent.futures.Future objects)
        self.count = 0 #keep track of job numbers for debuging
        self.job_id = 0 #assign and track unique job ids
        
        # API properties
        max_workers = int(config.mapping()['ConfluenceSpaceContent'].
                                get('RequestWorkers', DEFAULT_REQUEST_WORKERS))
        self.api_executer = ThreadPoolExecutor(max_workers = max_workers)
        self.api_session = FuturesSession(self.api_executer)
        
        self.api_base = \
            self.config['ConfluenceSpaceContent']['ConfluenceConnection']['url']
        self.api_limit = '&limit=' + \
                                config.mapping()['ConfluenceSpaceContent'].\
                                    get('ContentPaginationLimit', DEFAULT_PAGINATION_LIMIT)
        self.api_expand = '&expand=history,version,body.storage'
        
        # Content directives
        self.prune = datrie.Trie(string.printable) #make sure to not request same data twice from Confluence API
        self.content_get_history = \
            config.mapping()['ConfluenceSpaceContent'].get('SearchHistory', False)
        
        logger.debug(u"Threaded Confluence Mellon file provider initialized with {} worker threads".format(max_workers))
    
    def authorization_context(self):
        sec_context = component.createObject(u'mellon.authorization_context', )
        sec_context.identity = \
                self.config.mapping()['ConfluenceSpaceContent']['ConfluenceConnection'].get(
                        'username', '')
        sec_context.description = \
                self.config.mapping()['ConfluenceSpaceContent']['ConfluenceConnection'].get(
                        'context', '')
        return sec_context
    
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
            bin_checker = component.createObject(u"mellon_plugin.factory.confluence.attachment_bin_checker", item)
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
                    f = self.mellon_files.get_nowait()
                    component.getUtility(IApplyAuthorizationContext)(self.security_context, f)
                    yield f
            except Empty:
                pass
            time.sleep(.5)
        t.join()
        logger.debug('exiting asynchronous iteration queue publisher thread')

tsMellonFileProviderFromConfluenceConfigFactory = Factory(TSMellonFileProviderFromConfluenceConfig)
interface.alsoProvides(tsMellonFileProviderFromConfluenceConfigFactory, IMellonFileProviderFactory)
