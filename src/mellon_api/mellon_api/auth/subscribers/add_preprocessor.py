from zope import component
from zope.interface.interfaces import IRegistrationEvent
import mellon_api
from ..auth import api_authentication_preprocessor
    
from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(mellon_api.IFlaskApplication, IRegistrationEvent)
def inject_db_authentication(app, event):
    preprocessors = component.getUtility(
                        mellon_api.IFlaskRestApiPreprocessors, )
    preprocessors.append(api_authentication_preprocessor)
    logger.debug('injected authentication provider into api preprocessors')