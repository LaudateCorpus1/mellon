from zope import component
from zope import interface
from flask import abort
from . import IAuthenticationProvider, IUserPasswordAuthenticationManager
from .. import IFlaskRequest
from ..exc import ProcessingException
from . import exc
from .. import IFlaskApplication
from ..sa import ISASession
import binascii
from base64 import b64decode
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

def api_authentication_preprocessor(*args, **kwargs):
    #request = component.getUtility(IFlaskRequest)
    request = component.createObject(u"mellon_api.flask_request")
    auth_enabled = False
    for provider in component.subscribers([request], IAuthenticationProvider):
        auth_enabled = True
        try:
            provider()
            return # if it makes it here, then auth was ok
        except exc.MellonAPIAuthenticationException:
            pass
    if auth_enabled:
        from jsonapi.base.errors import Forbidden
        raise Forbidden
        #raise ProcessingException(description='Not Authorized', code=401)

@interface.implementer(IAuthenticationProvider)
@component.adapter(IFlaskRequest)
class BasicAuth(object):
    def __init__(self, context):
        self.context = context
        self.request = context
        self.manager = IUserPasswordAuthenticationManager(
                            component.getUtility(ISASession))
    
    def _get_authorization_header_value(self, request):
        for h in request.headers:
            if 'authorization' == h[0].lower():
                return h[1] if len(h) >= 2 else None
    
    def _get_encoded_authorization_entry(self, name, authorization_header_value):
        value = authorization_header_value.split(" ")
        if name.lower() == value[0].lower():
            return value[1] if len(value) >= 2 else None
    
    def _get_decoded_authorization_value(self, encoded_authorization_entry):
        bts = bytes(encoded_authorization_entry, encoding='latin-1')
        try:
            decoded_bytes = b64decode(bts)
        except binascii.Error:
            return
        return decoded_bytes.decode('latin-1')
    
    def _get_username_password_fields(self, decoded_authorization_value):
        authentication = decoded_authorization_value.split(':', 1)
        if len(authentication) < 2:
            authentication.append('')
        return tuple(authentication)
    
    def get_authentication_params(self):
        auth_entry = auth_value = None
        h_value = self._get_authorization_header_value(self.request)
        if h_value:
            auth_entry = self._get_encoded_authorization_entry('basic', h_value)
        if auth_entry:
            auth_value = self._get_decoded_authorization_value(auth_entry)
        if auth_value:
            return self._get_username_password_fields(auth_value)
        return ('','')
        
    
    def __call__(self):
        try:
            username, password = self.get_authentication_params()
            self.manager.check_authentication(username, password) # raises some form  of mellon_api.auth.exc.MellonAPIAuthenticationException
        except (KeyError, ValueError): # this fires on invalid users
            raise exc.MellonAPIAuthenticationException("invalid user specified")

@interface.implementer(IAuthenticationProvider)
@component.adapter(IFlaskRequest)
class TokenAuth(BasicAuth):
    
    def __init__(self, context):
        self.context = context
        self.request = context
        self.app = component.getUtility(IFlaskApplication)
        self.s = Serializer(self.app.config['SECRET_KEY'])
    
    def __call__(self):
        token = self.get_authentication_params()[0]
        try:
            self.s.loads(token, return_header=True)
        except SignatureExpired:
            raise exc.MellonAPITokenIsExpired()
        except BadSignature:
            raise exc.MellonAPIInvalidTokenSignature()
