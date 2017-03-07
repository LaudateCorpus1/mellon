from zope import interface
from mellon_plugin.reporter.sqlalchemy.orm import query

@interface.implementer(query.ISAResultRowModel)
class SAResultRowModel(object):
    def first(self, iface, row):
        for col in row:
            if iface.providedBy(col):
                return col
        raise ValueError("unable to find provider for {} in collection".format(iface))