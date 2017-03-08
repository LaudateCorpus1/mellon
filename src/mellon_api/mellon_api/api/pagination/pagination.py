from zope import component
from zope import interface
from mellon.mellon import get_registered_app
from mellon_api import IFlaskRequest
from . import IAPIRequestPage

@interface.implementer(IAPIRequestPage)
@component.adapter(IFlaskRequest)
class APIRequestPageFromFlaskRequest(object):
    def __init__(self, context): 
        m = get_registered_app()
        max_limit = m['vgetter'].get('ResourcePagination', 'max_limit', default=50)
        default_limit = m['vgetter'].get('ResourcePagination', 'max_limit', default=20)
                                        
        self.offset = context.args.get('offset', 0)
        self.limit = context.args.get('limit', default_limit)
        if self.limit > max_limit:
            self.limit = max_limit