from zope import interface
from zope import schema

class IAPIRequestSort(interface.Interface):
    sort = schema.ASCIILine(
                title=u"resource sorting request",
                description=u"see http://jsonapi.org/format/#fetching-sorting",
                required=True,
                readonly=True
            )