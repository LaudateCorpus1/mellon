from zope import component
from zope.interface.interfaces import IRegistrationEvent
import mellon_api
from ..auth import auth_func
    
from sparc.logging import logging
logger = logging.getLogger(__name__)

def _inject_auth_func(method):
    preprocessors = component.getUtility(
                        mellon_api.IFlaskRestApiPreprocessors, 
                        name=u"mellon_api.preprocessors_global")
    if method not in preprocessors:
        preprocessors[method] = []
    preprocessors[method].insert(0, auth_func)

@component.adapter(mellon_api.IFlaskApplication, IRegistrationEvent)
def inject_db_authentication(app, event):
    _inject_auth_func('POST')
    _inject_auth_func('GET_SINGLE')
    _inject_auth_func('GET_MANY')
    _inject_auth_func('PATCH_SINGLE') # covers PUT as well
    _inject_auth_func('PATCH_MANY') # covers PUT as well
    _inject_auth_func('DELETE_SINGLE')
    _inject_auth_func('DELETE_MANY')
    logger.debug('injected authentication provider into api preprocessors')