from zope import interface
from . import IFlaskRequest

@interface.implementer(IFlaskRequest)
class FlaskRequest(object):
    
    @property
    def request(self):
        from flask import request
        return request

flask_request = FlaskRequest()