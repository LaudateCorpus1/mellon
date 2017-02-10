from zope import component
import mellon_api

from sparc.logging import logging
logger = logging.getLogger(__name__)

def add_api_namespaces():
    api = component.queryUtility(mellon_api.IFlaskRestApiApplication)
    if not api:
        logger.debug('attempt to create api routes failed because no mellon_api.IFlaskRestApiApplication could be found in registry')
        return
    from .secrets import ns_secrets
    api.add_namespace(ns_secrets)