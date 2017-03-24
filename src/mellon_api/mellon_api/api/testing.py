from zope import component
import flask_restful
from marshmallow_jsonapi import fields
import mellon_api.api
from ..testing import MellonApiRuntimeLayer
from .schema import APISchemaMixin

class MellonApiResourceRuntimeLayer(MellonApiRuntimeLayer):
    
    def create_test_resources(self, count):
        for i in range(count):
            _resource = TestResource(id_=str(i+1), name=u'test resource {}'.format(i+1))
            TestResources[str(i+1)] = _resource
    
    def reset_test_resources(self):
        for k in [k for k in TestResources.keys()]:
            del TestResources[k]
    
    def get_resource_count(self):
        return len(TestResources.keys())

    def setUp(self, config=None):
        _config = {}
        if config:
            _config.update(config)
        self.config = _config
        super(MellonApiResourceRuntimeLayer, self).setUp(config=_config)
        
        #Add test resource endpoint to api
        endpoint_type = TestResourceSchema.Meta.type_
        endpoint = endpoint_type + 's'
        urls = ['/'+endpoint, '/'+endpoint+'/<resource_id>']
        self.rest_api.add_resource(APITestResource, *urls, endpoint=endpoint)
    
    def tearDown(self):
        self.reset_test_resources() #actually, this should be done in the test teardowns...not the layer
        super(MellonApiRuntimeLayer, self).tearDown()
MELLON_API_RESOURCE_RUNTIME_LAYER = MellonApiResourceRuntimeLayer(mellon_api.api)

TestResources = {}

class TestResource(object):
    def __init__(self, id_, name):
        self.id = id_
        self.name = name

class TestResourceSchema(APISchemaMixin):
    id = fields.Str(dump_only=True)
    name = fields.Str()   
    
    class Meta:
        type_ = 'test-resource'
        strict = True
        self_url_many =  '/test-resources/'
        self_url = '/test-resources/{resource_id}'
        self_url_kwargs = {'resource_id': '<id>'}

class APITestResource(flask_restful.Resource):
    mm_schema = TestResourceSchema
    
    def _get_model_or_404(self, model_id):
        resource = TestResources.get(model_id, None)
        if not resource:
            flask_restful.abort(404, message="{} doesn't exist".format(model_id))
        return resource
    
    def get(self, resource_id=None):
        if resource_id:
            model = self._get_model_or_404(resource_id)
            return self.mm_schema().dump(model).data
        else:
            _request = component.createObject(u"mellon_api.flask_request")
            page_r = component.createObject(
                    u"mellon_api.api.pagination.page_request_from_request_and_count",
                    _request, len(TestResources.keys()))
            _result = [TestResources[r] for r in sorted(TestResources.keys())][page_r.offset:page_r.limit]
            return self.mm_schema(many=True).dump(_result).data