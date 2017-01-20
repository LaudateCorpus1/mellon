from zope import component
from zope import interface
import importlib
from hashlib import md5
import mellon
import scrapy
from scrapy.linkextractors import LinkExtractor
import scrapy.spiders
try:
    from urllib import parse
except ImportError:
    import urlparse as parse # Py2

from sparc.configuration import container
from mellon_plugin.factory import web_crawler
from mellon_plugin.factory.web_crawler.web_crawler.items import WebCrawlerItem

from sparc.logging import logging
logger = logging.getLogger(__name__)

"""
How to connect IMellonFileProviderFactory (which produces IMellonFileProvider
objects) to:
 - a crawler process which contains one or more spiders
 
How to create a CrawlerSpider implementation that can take runtime config
parameters to define unique types (probably using the Python type() call)

How to define and deliver spider settings.  Should try to make this native.
Looks like we could easily allow setting definition in YAML and pass it
into type creation at runtime for spider-specific stuff.  For project level,
not yet sure how API launch would look for it...might be env variable to 
a settings.py file

Figure out how/when to run spiders concurrently vs sequentially (probably
has to do with mellon yaml config and factory definitions in file...

How to define a factory...1-to-1 of spider to factory or many-to-one (prefer the 2nd).
Need way to define spiders where mellon config can deliver all possible 
configs (see CrawlerSpider to understand what options are there)

Might want to be able enable use of base spider types defined by Scrapy with
mellon yaml options.  Also allow create interfaces and base classes to allow
custom spider definitions...hmm..think about this one.


We may want to have Spiders registered via ISpider marker, then have mellon
pick these up via subscriber lookup <--we'd probably run all spiders in a 
single process...might not be the way to go (memory usage?)...we should at
least provide some mechanism to create multiple processes to run spiders.
"""

class MellonSpiderMixin(scrapy.spiders.CrawlSpider):
    rules = (scrapy.spiders.Rule(LinkExtractor(
                                               deny_extensions=[],
                                               unique=True), 
                                        callback='parse_item'),)
    
    def parse_start_url(self, response):
        if hasattr(self, 'auth_form_data'):
            # see https://doc.scrapy.org/en/latest/topics/request-response.html#topics-request-response-ref-request-userlogin
            return scrapy.FormRequest.from_response(
                    response,
                    formdata=self.auth_form_data,
                    callback=self.parse_item) 
        return self.parse_item(response)
    
    def parse_item(self, response):
        item = WebCrawlerItem()
        item['response'] = response
        return item
    

def ScrapySimpleMellonWebsiteCrawlerTypeFromConfigFactory(config):
    """Create new types whose base is scrapy.spiders.CrawlSpider
    
    Allows dynamic CrawlSpider types to be created based on inputs.  We need
    this because scrapy's method of running is to look for runtime types that
    inherit from scrapy.spiders.Spider.  We have this factory to allow folks
    to crawl based on a runtime config, not runtime code.
    
    Args:
        config: sparc.configuration.container.ISparcAppPyContainerConfiguration
                values of ScrapySimpleTextWebsiteCrawler yaml def.
    """
    # get base type information by grabbing first urls entry
    type_url_info = parse.urlparse(config['urls'][0])
    type_dict = \
        {'name': type_url_info.netloc,
         #'allowed_domains': [parse.urlparse(url).netloc for url in config['urls']],
         'start_urls' : config['urls'],
         'custom_settings': {}
         }
    if 'ScrapyFormData' in config:
        type_dict['auth_form_data'] = config['ScrapyFormData']
    if 'attributes' in config:
        type_dict.update(config['attributes'])
    if 'ScrapySettings' in config:
        type_dict['custom_settings'] = config['ScrapySettings']
    if 'RulesListFactory' in config:
        _callable = importlib.import_module(config['RulesListFactory'])
        type_dict['rules'] = _callable()
    
    _type_name_md5 = md5()
    _type_name_md5.update(config['urls'][0].encode('utf-8'))
    return type('ScrapySimpleTextWebsiteCrawler_'\
                        +_type_name_md5.hexdigest(),
                                    (MellonSpiderMixin,), 
                                    type_dict)

"""
We need to dynamically create Spider types based on yaml config information.
In addition, we need to make these type available in 2 areas:
 - We need to add them to this module's namespace in order for the Scrapy 
   CLI app to find them
 - We need to add them to the component registry, so the 
   IMellonFileProviderFactory implementation can find them

Note:
  This only works within a Mellon runtime environment (e.g. there is a
  component registry with a mellon.IMellonApplication registered utility
"""
Mellon = component.getUtility(mellon.IMellonApplication)
v_iter = component.getUtility(container.ISparcPyDictValueIterator)
for d in v_iter.values(Mellon.get_config(), 'ScrapySimpleTextWebsiteCrawler'):
    new_crawler_type = ScrapySimpleMellonWebsiteCrawlerTypeFromConfigFactory(d)
    interface.alsoProvides(new_crawler_type, web_crawler.IScrapySpider)
    globals()[new_crawler_type.__name__] = new_crawler_type
    sm = component.getSiteManager()
    sm.registerUtility(new_crawler_type, web_crawler.IScrapySpider, name=new_crawler_type.name) #give components access to app config
    logger.info("Registered new spider for ScrapySimpleTextWebsiteCrawler: {}".format(new_crawler_type.name))