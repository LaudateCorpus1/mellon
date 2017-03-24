from zope import component
from zope.interface.interfaces import IRegistrationEvent
import mellon_api
import jsonapi.sqlalchemy
from .. import schema, IAPISAEndpoints
from mellon_plugin.reporter.sqlalchemy.orm import models

from sparc.logging import logging
logger = logging.getLogger(__name__)

def add_endpoint(model, schema, resource):
    #create IAPISAEndpoint
    api = component.getUtility(mellon_api.IFlaskRestApiApplication)
    _endpoint = schema.Meta.type_ + 's'
    routes = ['/'+_endpoint, '/'+_endpoint+'/<resource_id>']
    endpoint = component.createObject(u'mellon_api.api.sa_endpoint',
                                      model, resource, schema, routes, _endpoint)
    
    #add new Flask endpoint with routes
    api.add_resource(endpoint.resource, *endpoint.routes, endpoint=endpoint.endpoint)
    #register to IAPISAEndpoints to enable easier lookups of stuff
    endpoints = component.getUtility(IAPISAEndpoints)
    endpoints.map[endpoint.endpoint] = endpoint
    
    logger.debug("New endpoint {} with urls {} added to api".format(endpoint.endpoint, endpoint.routes))

@component.adapter(mellon_api.IFlaskRestApiApplication, IRegistrationEvent)
def register_endpoints(app, event):
    api = component.getUtility(mellon_api.IFlaskRestApiApplication)
    #authorization-context
    #resource = component.createObject(u"mellon_api.api.resource_type",
    #                                       models.AuthorizationContext,
    #                                       schema.AuthorizationContextSchema)
    #add_endpoint(models.AuthorizationContext,schema.AuthorizationContextSchema, resource)
    api.add_type(jsonapi.sqlalchemy.Schema(models.AuthorizationContext))
    