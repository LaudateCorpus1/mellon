from zope import interface
from zope import schema

class IAPIRequestFilter(interface.Interface):
    filter = schema.TextLine(
                title=u"URI encoded resource filter JSON string",
                required=True,
                readonly=True
            )