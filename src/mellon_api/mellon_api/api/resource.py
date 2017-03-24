from zope import component
from zope.component.factory import Factory
from zope import interface
from zope.interface.exceptions import Invalid
import flask_restful
from mellon_api import sa
from mellon_plugin.reporter.sqlalchemy.orm import ISAModel

from .pagination import IAPIPagination
from . import IAPIRequestResourceInclude, IMMSchema, IAPISAEndpointLookup
import mellon_api
"""
JSONAPI Interfaces

links:
 self:
 first:
 last:
 prev:
 next:
data:
 id:
 type:
 attributes:
 relationships:
included:


"""

@interface.implementer(IAPIRequestResourceInclude)
@component.adapter(mellon_api.IFlaskRequest)
class APIRequestResourceIncludeFromFlaskRequest(object):
    def __init__(self, context):
        self.include = context.args.get('include', '')

class APISAORMResourceBase(flask_restful.Resource):
    
    sa_model = None
    mm_schema = None
    
    def _get_model_or_404(self, model_id):
        session = component.getUtility(sa.ISASession)
        model = session.query(self.sa_model).get(model_id)
        if not model:
            flask_restful.abort(404, message="{} doesn't exist".format(model_id))
        return model
    
    def _get_inclusion_list_or_400(self):
        rel_manager = component.createObject(
            u"mellon_plugin.reporter.sqlalchemy.orm.query.orm_related_models")
        rel_manager.inject(self.sa_model)
        try:
            include = IAPIRequestResourceInclude(component.createObject(u"mellon_api.flask_request"))
            if include:
                looker = component.getUtility(IAPISAEndpointLookup)
                for dotted_list in include.split(','):
                    for type_ in dotted_list.split('.'):
                        endpoint = looker.lookup(type_)
                        
        except LookupError as e:
            flask_restful.abort(400, message="{}".format(e))
        return rel_manager.models()
        
        
    
    def _set_response_pagination(self, request, count):
        """Setup pagination on the response object as annotations.  best way I
        could think to get the info over to the schema marshaler.  bit of a hack.
        """
        page = component.createObject(
                    u"mellon_api.api.pagination.pagination_from_request_and_count",
                    request, count)
        response_page = IAPIPagination(request)
        response_page.first = page.first
        response_page.last = page.last
        response_page.prev = page.prev
        response_page.next = page.next
    
    def get(self, resource_id=None):
        """
        JSONAPI implementation
            jsonapi:
            errors:
            data:
             type:
             id:
             attributes:
             relationships:
              data:
             links:
            links:
             self:
             related:
            included:
        """
        if resource_id:
            model = self._get_model_or_404(resource_id)
            return self.mm_schema().dump(model).data
        else:
            #see mellon_plugin.reporter.sqlalchemy.orm.query.query.txt
            session = component.getUtility(sa.ISASession)
            request = component.createObject(u"mellon_api.flask_request")
            #THIS IS A WORK-IN-PROGRESS...IT NEEDS HELP
            q = session.query(self.sa_model)
            count = q.count()
            self._set_response_pagination(request, count)
            page_r = component.createObject(
                    u"mellon_api.api.pagination.page_request_from_request_and_count",
                    request, count)
            offset = page_r.offset
            if offset < 0 or offset >= count:
                offset = 0
            _result = q.slice(offset, page_r.limit)
            return self.mm_schema(many=True).dump(_result).data


def create_flask_api_resource_type(sa_model, mm_schema):
    if not ISAModel.implementedBy(sa_model):
        raise Invalid("expected {} to implement {}".format(sa_model, ISAModel))
    if not IMMSchema.implementedBy(mm_schema):
        raise Invalid("expected mm_schema {} to implement {}".format(mm_schema, IMMSchema))

    _type = type('APISAResource'+sa_model.__name__, (APISAORMResourceBase,), 
                                {'sa_model': sa_model, 'mm_schema': mm_schema})
    interface.classImplements(_type, mellon_api.IFlaskRestApiResource)
    return _type
flask_api_resource_type_factory = Factory(create_flask_api_resource_type)