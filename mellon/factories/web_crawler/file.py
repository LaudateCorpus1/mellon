import io
import threading
import time
from twisted.internet import reactor
from zope import component
from zope.component.factory import Factory
from zope import interface
from scrapy.crawler import CrawlerRunner
import mellon
import mellon.file
from .interfaces import IScrapySpider
from mellon.factories.web_crawler.web_crawler import pipelines

try:
    from Queue import Empty
except ImportError:
    from queue import Empty

class MellonByteFileFromItemAndConfig(mellon.file.MellonByteFileFromFileStreamAndConfig):
    
    def __init__(self, item, config):
        self.url = item['response'].url
        super(MellonByteFileFromItemAndConfig, self).__init__(io.BytesIO(item['response'].body), config)
    
    def __str__(self):
        return "byte file at location {}".format(self.url)
mellonByteFileFromItemAndConfigFactory = Factory(MellonByteFileFromItemAndConfig)

class MellonUnicodeFileFromItemAndConfig(mellon.file.MellonUnicodeFileFromFileStreamAndConfig):
    
    def __init__(self, item, config):
        self.url = item['response'].url
        super(MellonUnicodeFileFromItemAndConfig, self).__init__(io.StringIO(item['response'].body_as_unicode()), config)
    
    def __str__(self):
        return "unicode file at location {}".format(self.url)
mellonUnicodeFileFromItemAndConfigFactory = Factory(MellonUnicodeFileFromItemAndConfig)


def run_once(func):
    "A decorator that runs a function only once."
    def decorated(*args, **kwargs):
        try:
            return decorated._once_result
        except AttributeError:
            decorated._once_result = func(*args, **kwargs)
            return decorated._once_result
    return decorated

@run_once
def run_spiders():
    sm = component.getSiteManager()
    runner = CrawlerRunner()
    for name, spider in sm.getUtilitiesFor(IScrapySpider):
        pipeline_setting = {
            'mellon.factories.web_crawler.web_crawler.pipelines.WebCrawlerQueuePipeline': 0}
        if spider.custom_settings and 'ITEM_PIPELINES' in spider.custom_settings:
            spider.custom_settings.update(pipeline_setting)
        else:
            spider.custom_settings['ITEM_PIPELINES'] = pipeline_setting
        runner.crawl(spider)
    if runner.crawlers:
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run(installSignalHandlers=0) #blocks while adding scrapy items into queue via pipeline
            
            
@interface.implementer(mellon.IMellonFileProvider)
class MellonFileProviderForAllRegisteredScrapySpiders(object):
    """
    Since Scrapy is really intended to be an app, it incapsulates/blocks while
    it scrapes.  We want to stream as it scrapes...so we'll:
     - start scrapy in a thread
       - leverage web_crawler thread-safe queue pipeline publisher
     - in the main thread, we'll read + yield/stream from the queue
    """
    
    def __init__(self, config):
        self.config = config
    

    def __iter__(self):
        """Effectively, this can only be iterated over once class-wide.  This
        is due to complexities involved in trying to get a Mellon File
        provider integrated appropriately to a Twisted reactor (Scrapy uses
        Twisted for async io ops)...didn't have time to do it :(
        """
        t = threading.Thread(target=run_spiders)
        t.daemon = True
        t.start()
        while not pipelines.WebCrawlerPipelineItems.empty() or t.is_alive():
            try:
                item = pipelines.WebCrawlerPipelineItems.get_nowait()
                if mellon.IBinaryChecker(item['response']).check():
                    yield component.createObject(\
                        u'mellon.factories.web_crawler.byte_file',
                        item, self.config)
                else:
                    yield component.createObject(\
                        u'mellon.factories.web_crawler.unicode_file',
                        item, self.config)
            except Empty:
                pass
            time.sleep(2)
        t.join()

mellonFileProviderForAllRegisteredScrapySpidersFactory = Factory(MellonFileProviderForAllRegisteredScrapySpiders)
interface.alsoProvides(MellonFileProviderForAllRegisteredScrapySpiders, mellon.IMellonFileProviderFactory)
