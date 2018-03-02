from zope import component
from zope import interface
from sparc.login.credentials import ICredentialIdentity
from sparc.login.credentials.authn import IPasswordHashToken
from sparc.login.credentials.authn.crypt import ICrypter
from sparc.login.credentials.exceptions import UnknownIdentity
from mellon_gui.sa import ISASession
from . import models

@interface.implementer(IPasswordHashToken)
@component.adapter(ICredentialIdentity)
class SAPasswordHashToken(object):
    
    def __init__(self, context):
        self.context = context
        session = component.getUtility(ISASession)
        self.user = session.query(models.UserPasswordAuthentication).get(self.context.getId())
        if not self.user:
            raise UnknownIdentity("username does not exist.")
    
    @property
    def token(self):
        return self.user.password_crypt
    
    @token.setter
    def token(self, value):
        crypter = component.getUtility(ICrypter)
        self.user.password_crypt = crypter.hash(value.encode('utf-8'))
