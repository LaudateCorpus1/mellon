from zope import component
from flask_restplus import Resource
import mellon_api

from sparc.logging import logging
logger = logging.getLogger(__name__)
api = component.getUtility(mellon_api.IFlaskRestApiApplication)

endpoint = '/secrets'
logger.debug("registering {} api resource route".format(endpoint))
@api.route(endpoint)
class Secrets(Resource):
    def get(self):
        return {'hello': 'world'}