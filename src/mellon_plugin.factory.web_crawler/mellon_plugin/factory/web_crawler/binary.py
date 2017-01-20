from zope import component
from zope import interface
import mellon
from .interfaces import IScrapyHttpResponse

@interface.implementer(mellon.IBinaryChecker)
@component.adapter(IScrapyHttpResponse)
class BinaryCheckerForScrapyHttpResponse(object):
    
    def __init__(self, context):
        self.context = context # scrapy http response object
    
    def check(self):
        """Scrapy Item encoding based check for binary data"""
        if hasattr(self.context, 'encoding') and self.context.encoding:
            return False
        return True