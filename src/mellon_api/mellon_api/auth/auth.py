from zope import component
from zope import interface
from . import IAuthenticationProvider, IUserPasswordAuthenticationManager
from .. import IFlaskRequest
from flask_restless import ProcessingException
from . import exc
from ..sa import ISASession
import binascii
from base64 import b64decode

def api_authentication_preprocessor(*args, **kwargs):
    try:
        request = component.getUtility(IFlaskRequest)
        auth_enabled = False
        for provider in component.subscribers([request], IAuthenticationProvider):
            auth_enabled = True
            provider()
            return # if it makes it here, then auth was ok
    except exc.MellonAPIAuthenticationException:
        pass
    if auth_enabled:
        raise ProcessingException(description='Not Authorized', code=401)

@interface.implementer(IAuthenticationProvider)
@component.adapter(IFlaskRequest)
class BasicAuth(object):
    def __init__(self, context):
        self.context = context
        self.request = context.request
        self.manager = IUserPasswordAuthenticationManager(
                            component.getUtility(ISASession))
    
    def _get_authorization_header_value(self, request):
        for h in request.headers:
            if 'authorization' == h[0].lower():
                return h[1] if len(h) >= 2 else None
    
    def _get_encoded_authorization_entry(self, authorization_header_value):
        value = authorization_header_value.split(" ")
        if 'basic' == value[0].lower():
            return value[1] if len(value) >= 2 else None
    
    def _get_decoded_authorization_value(self, encoded_authorization_entry):
        bts = bytes(encoded_authorization_entry, encoding='latin-1')
        try:
            decoded_bytes = b64decode(bts)
        except binascii.Error:
            return
        return decoded_bytes.decode('latin-1')
    
    def _get_username_password(self, decoded_authorization_value):
        authentication = decoded_authorization_value.split(':', 1)
        if len(authentication) < 2:
            authentication.append('')
        return authentication
    
    def __call__(self):
        username, password = '', ''
        auth_entry = auth_value = None
        h_value = self._get_authorization_header_value(self.request)
        if h_value:
            auth_entry = self._get_encoded_authorization_entry(h_value)
        if auth_entry:
            auth_value = self._get_decoded_authorization_value(auth_entry)
        if auth_value:
            username, password = self._get_username_password(auth_value)
        
        try:
            self.manager.check_authentication(username, password) # raises some form  of mellon_api.auth.exc.MellonAPIAuthenticationException
        except KeyError: # this fires on invalid users
            raise exc.MellonAPIAuthenticationException("invalid user specified") 
