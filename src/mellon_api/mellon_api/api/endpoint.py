from zope import component
from zope import interface
from zope.component.factory import Factory
from . import IAPISAEndpoint, IAPISAEndpoints, IAPISAEndpointLookup

@interface.implementer(IAPISAEndpoints)
class APISAEndpoints(object):
    def __init__(self):
        self.map = {}

@interface.implementer(IAPISAEndpoint)
class APISAEndpoint(object):
    def __init__(self, model, resource, schema, routes, endpoint):
        self.model = model
        self.resource = resource
        self.schema = schema
        self.routes = routes
        self.endpoint = endpoint
APISAEndpointFactory = Factory(APISAEndpoint)

@interface.implementer(IAPISAEndpointLookup)
class APISAEndpointLookup(object):
    def lookup(self, entry):
        endpoints = component.getUtility(IAPISAEndpoints)
        
        for endpoint in endpoints.map.values():
            if endpoint.schema.Meta.type_ == entry:
                return endpoint
        
        raise LookupError("entry {} not available".format(entry))