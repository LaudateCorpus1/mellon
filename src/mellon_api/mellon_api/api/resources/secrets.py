from zope import component
from flask_restplus import Resource
import mellon_api

from sparc.logging import logging
logger = logging.getLogger(__name__)
api = component.getUtility(mellon_api.IFlaskRestApiApplication)

ns_secrets = api.namespace('secrets', description="View and update Mellon Secret workflow information")

route = '/'
logger.debug("registering {}{} api resource route".format(ns_secrets.name,route))
@ns_secrets.route(route)
class Secrets(Resource):
    def get(self):
        return {'hello': 'world'}