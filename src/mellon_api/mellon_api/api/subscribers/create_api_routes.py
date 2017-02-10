from zope import component
from zope.interface.interfaces import IRegistrationEvent
from mellon_api import IFlaskRestApiApplication
from ..resources import add_api_namespaces

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(IFlaskRestApiApplication, IRegistrationEvent)
def add_api_routes(api, event):
    logger.debug('loading api routes ...')
    add_api_namespaces()
    logger.debug('completed api route loading.')