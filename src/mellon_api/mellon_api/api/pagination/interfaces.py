from zope import interface
from zope import schema

class IAPIRequestPage(interface.Interface):
    offset = schema.Int(
                title=u"Ordered resources to skip",
                required=True,
                readonly=True
            )
    limit = schema.Int(
                title=u"Limit on available resources to return",
                required=True,
                readonly=True
            )
    

class IAPIPagination(interface.Interface):
    """API Pagination information"""
    first = schema.TextLine(
                title=u"the first page of data",
                required=True,
                readonly=True
            )
    last = schema.TextLine(
                title=u"the last page of data",
                required=True,
                readonly=True
            )
    prev = schema.TextLine(
                title=u"the previous page of data",
                required=False,
                readonly=True
            )
    next = schema.TextLine(
                title=u"the next page of data",
                required=False,
                readonly=True
            )