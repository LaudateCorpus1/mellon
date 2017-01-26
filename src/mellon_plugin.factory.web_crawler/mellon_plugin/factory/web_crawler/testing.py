import os.path
import threading
import mellon
from mellon.mellon import create_and_register_app
from mellon_plugin.factory.web_crawler import tests
from mellon_plugin.factory.web_crawler.web_crawler.pipelines import WebCrawlerPipelineItems
from mellon_plugin.factory.web_crawler.file import run_spiders
from mellon_plugin.factory.web_crawler.file import mellonFileProviderForAllRegisteredScrapySpidersFactory
from mellon.testing import MellonApplicationRuntimeLayer

try:
    import SocketServer as socketserver
    import SimpleHTTPServer as http_server
    from Queue import Empty
except ImportError:
    import socketserver
    import http.server as http_server
    from queue import Empty

class MellonWebCrawlerRuntimeLayer(MellonApplicationRuntimeLayer):
    """
    Provides a runtime httpd server that publishes the web_crawler.tests:httpd_root 
    directory via Pythons SimpleHTTPRequestHandler module
    """
    http_port = 9080
    
    def start_http_server(self):
        Handler = http_server.SimpleHTTPRequestHandler
        self.httpd_server = socketserver.TCPServer(("", self.http_port), Handler)
        self.server_thread = threading.Thread(target=self.httpd_server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def shutdown_http_server(self):
        self.httpd_server.shutdown()
        self.httpd_server.server_close()
    
    def setUp(self):
        self.config = {'MellonSnippet':
                          {
                           'lines_coverage': 2,
                           'lines_increment': 1,
                           'bytes_read_size': 8,
                           'bytes_coverage': 4,
                           'bytes_increment': 3
                           },
                       'ScrapySimpleTextWebsiteCrawler':
                           {
                            'urls': ['http://localhost:{}/index.html'.format(self.http_port)]
                           },
                        'ZCMLConfiguration':
                            [{'package':'mellon_plugin.factory.web_crawler'}]
                      }
        self.cwd = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(tests.__file__), 'httpd_root'))
        self.start_http_server() # non-blocking (starts httpd server in a thread)
        super(MellonWebCrawlerRuntimeLayer, self).setUp()
    
    def tearDown(self):
        self.shutdown_http_server()
        os.chdir(self.cwd)
        super(MellonWebCrawlerRuntimeLayer, self).tearDown()
    
MELLON_FACTORY_WEB_CRAWLER_LAYER = MellonWebCrawlerRuntimeLayer(mellon)

class MellonWebCrawlerExecutedRuntimeLayer(MellonWebCrawlerRuntimeLayer):
    """
    Provides the results of an executed webcrawler.  This should be used
    to avoid testing issues related to multiple calls to running a twisted
    reactor (which won't work).  This class should be used for those test
    cases
    """
    
    item_queue = [] # keep list of web_crawler item queue for testing reference
    mellon_files = [] # keep list of Mellon files for testing reference
    
    def _repopulate_pipeline_queue(self):
        for i in MellonWebCrawlerExecutedRuntimeLayer.item_queue:
            WebCrawlerPipelineItems.put(i)
    
    
    def get_item_by_name(self, name):
        for item in self.item_queue:
            if item['response'].url.endswith(name):
                return item

    def get_file_by_name(self, name):
        for f in self.mellon_files:
            if str(f).endswith(name):
                return f

    def setUp(self):
        MellonWebCrawlerRuntimeLayer.setUp(self)
        app = create_and_register_app(self.config, self.verbose, self.debug)
        run_spiders() #will fill up the web_crawler item queue
        try:
            while True:
                item = WebCrawlerPipelineItems.get_nowait()
                MellonWebCrawlerExecutedRuntimeLayer.item_queue.append(item)
        except Empty:
            self._repopulate_pipeline_queue()
        
        mfp = mellonFileProviderForAllRegisteredScrapySpidersFactory(app.get_config())
        MellonWebCrawlerExecutedRuntimeLayer.mellon_files = [f for f in mfp]
        MellonWebCrawlerExecutedRuntimeLayer.class_is_setup = True
    
MELLON_FACTORY_EXECUTED_WEB_CRAWLER_LAYER = MellonWebCrawlerExecutedRuntimeLayer(mellon)