from zope import component
from zope import interface
from marshmallow_jsonapi import Schema
from marshmallow_jsonapi import fields
from .pagination import IAPIPagination

from mellon_plugin.reporter.sqlalchemy.orm import interfaces as orm_iface
from . import IMMSchema, IMMSchemaMeta

class APISchemaMixin(Schema):
    def get_top_level_links(self, data, many):
        links = Schema.get_top_level_links(self, data, many)
        if many:
            r = component.createObject(u"mellon_api.flask_request")
            pag = IAPIPagination(r)
            if pag.first:
                links['first'] = pag.first
            if pag.last:
                links['last'] = pag.last
            if pag.prev:
                links['prev'] = pag.prev
            if pag.next:
                links['next'] = pag.next
        return links

def Meta(type_):
    meta = {}
    meta['type_'] = type_
    meta['strict'] = True
    #meta['self_url_many'] = '/'+type_+'s/'
    #meta['self_url'] = meta['self_url_many']+'{resource_id}'
    #meta['self_url_kwargs'] = {'resource_id': '<id>'}
    meta['self_view'] = '/'+type_+'s/'
    meta['self_view_kwargs'] = {'resource_id': '<id>'}
    meta['self_view_many'] = meta['self_view']
    
    meta_type = type('Meta', (), meta)
    interface.classImplements(meta_type, IMMSchemaMeta)
    return meta_type
    

@interface.implementer(IMMSchema, orm_iface.IORMAuthorizationContext)
class AuthorizationContextSchema(APISchemaMixin):
    Meta = Meta('authorization-context')
    id = fields.Str(dump_only=True)
    name = fields.Str()
    description = fields.Str()

    
        
