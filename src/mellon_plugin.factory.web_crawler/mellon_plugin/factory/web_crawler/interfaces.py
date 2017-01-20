from zope import interface

class IScrapySpider(interface.Interface):
    """Marker for scrapy.spiders.Spider"""

class IScrapyHttpResponse(interface.Interface):
    """Marker for scrapy.http.response.Response"""