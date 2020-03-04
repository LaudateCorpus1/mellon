from zope import component
from zope import interface
from zope import schema
from zope.component.factory import Factory
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAnnotatable
from flask import url_for
from mellon.mellon import get_registered_app
from . import IAPIRequestPage, IAPIPagination

@interface.implementer(IAPIRequestPage)
class APIRequestPageFromFlaskRequestAndCount(object):
    def __init__(self, request, count): 
        m = get_registered_app()
        max_limit = m['vgetter'].get_value('ResourcePagination', 'max_limit', default=50)
        default_limit = m['vgetter'].get_value('ResourcePagination', 'max_limit', default=20)
                                        
        self.offset = int(request.args.get('offset', 0))
        if self.offset < 0 or self.offset >= count:
            self.offset = 0
        self.limit = int(request.args.get('limit', default_limit))
        if self.limit > max_limit:
            self.limit = max_limit
APIRequestPageFromFlaskRequestAndCountFactory = Factory(APIRequestPageFromFlaskRequestAndCount)

@interface.implementer(IAPIPagination)
class APIPaginationFromRequestAndCount(object):
    def __init__(self, request, count):
        self.request = request
        self.count = count
        self.endpoint = request.url_rule.endpoint
        page_r = APIRequestPageFromFlaskRequestAndCount(request, count)
        if page_r.offset <= 0:
            self.offset = 0
        else:
            self.offset = page_r.offset if count - page_r.offset > 0 else 0
        self.limit = page_r.limit
        self._offset_pointer = self.offset # we use this variable for testing
    
    @property
    def first(self):
        args = dict(self.request.args)
        self._offset_pointer = 0
        args['offset'] = self._offset_pointer
        return url_for(self.endpoint, **args)
    
    @property
    def last(self):
        args = dict(self.request.args)
        m = self.count % self.limit
        if m:
            self._offset_pointer = (self.count - 1) - m #(last index) minus remainder
            args['offset'] = self._offset_pointer
            return url_for(self.endpoint, **args)
        else:
            self._offset_pointer = (self.count - 1) - self.limit # (last index) minus limit
            args['offset'] = self._offset_pointer
            if args['offset'] > 0:
                return url_for(self.endpoint, **args)
    
    @property
    def prev(self):
        if self.offset:
            args = dict(self.request.args)
            _offset = self.offset - self.limit
            self._offset_pointer = _offset if _offset >= 0 else 0
            args['offset'] = self._offset_pointer
            return url_for(self.endpoint, **args)
    
    @property
    def next(self):
        """
        l = [1,2,3]
        current = l[0]
        limit = 2
        new = current + limit = 2 (ok because 2 < len(l))
        
        current = l[1]
        new = 1+2 = 3 (not ok because 3 >= len(l)
        """
        if self.offset + self.limit < self.count:
            args = dict(self.request.args)
            self._offset_pointer = self.offset + self.limit
            args['offset'] = self._offset_pointer
            return url_for(self.endpoint, **args)
            
APIPaginationFromRequestAndCountFactory = Factory(APIPaginationFromRequestAndCount)

@interface.implementer(IAPIPagination)
@component.adapter(IAnnotatable)
class APIPaginationFromFlaskRequest(object):
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context).\
                                setdefault('IAPIPagination', {})
        for prop in ['first','last','prev','next']:
            self.annotations.setdefault(prop, None)
    
    @property
    def first(self):
        return self.annotations['first']
    @first.setter
    def first(self, value):
        schema.getFields(IAPIPagination)['first'].validate(value)
        self.annotations['first'] = value
    
    @property
    def last(self):
        return self.annotations['last']
    @last.setter
    def last(self, value):
        schema.getFields(IAPIPagination)['last'].validate(value)
        self.annotations['last'] = value
    
    @property
    def next(self):
        return self.annotations['next']
    @next.setter
    def next(self, value):
        schema.getFields(IAPIPagination)['next'].validate(value)
        self.annotations['next'] = value
    
    @property
    def prev(self):
        return self.annotations['prev']
    @prev.setter
    def prev(self, value):
        schema.getFields(IAPIPagination)['prev'].validate(value)
        self.annotations['prev'] = value