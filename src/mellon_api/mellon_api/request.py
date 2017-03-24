from zope import interface
from zope.component.factory import Factory
from zope.annotation.interfaces import IAttributeAnnotatable
from . import IFlaskRequest

@interface.implementer(IFlaskRequest)
class FlaskRequest(object):
    def __new__(self):
        from flask import request
        #request is a proxy....we need the real object
        _request = request._get_current_object()
        interface.alsoProvides(_request, IFlaskRequest, IAttributeAnnotatable)
        return request
FlaskRequestFactory = Factory(FlaskRequest)