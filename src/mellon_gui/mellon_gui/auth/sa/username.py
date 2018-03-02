import random, string
from zope import component
from zope import interface

from sparc.login.credentials import ICredentialIdentity
from sparc.login.credentials import ICredentialIdentityManager
from sparc.login.identification import IIdentified
from sparc.login.identification.exceptions import InvalidIdentification
from sparc.login.principal import IPrincipalManager, IPrincipal
from mellon_gui.sa import ISASession
from . import models

@interface.implementer(IPrincipal)
@component.adapter(ICredentialIdentity)
class PrincipalFromCredentialIdentity(object):
    def __new__(cls, context):
        session = component.getUtility(ISASession)
        user = session.query(models.UserPasswordAuthentication).get(context.getId())
        if not user:
            raise TypeError('unable to adapt.  credential identity does not exist in db {}'.format(context))
        return component.createObject(u'sparc.login.principal', user.principal_id)


@interface.implementer(ICredentialIdentityManager)
class SessionCredentialIdentityManager(object):
    
    def _resolve(self, identifier):
        return identifier.getId() if IIdentified.providedBy(identifier) else identifier
    
    def _get_model(self, identifier):
        session = component.getUtility(ISASession)
        user = session.query(models.UserPasswordAuthentication).get(self._resolve(identifier))
        if not user:
            raise InvalidIdentification("specified user does not exist {}".format(identifier))
        return user
    
    def generate(self, hint=None):
        """Generates and returns a new IIdentity provider
        
        Args:
            hint: String hint to base new identity on.  Implementers may ignore
                  this argument.
        """
        length = 8
        
        hint = hint if hint != None else ''.join(random.choice(string.ascii_lowercase) for i in range(length))
        try:
            return self.create(hint)
        except InvalidIdentification:
            pass
        
        i = 1
        while True:
            try:
                return self.create(hint + str(i))
            except InvalidIdentification:
                i += 1
            
        
    def create(self, id_token):
        """Creates and returns a new IIdentity provider
        
        Args:
            id_token: Assign identifier String as unique identifier.
        
        Raises:
            InvalidIdentification if identifier is not valid
        """
        if self.contains(id_token):
            raise InvalidIdentification("specified user already exists {}".format(id_token))
            
        session = component.getUtility(ISASession)
        principals = component.getUtility(IPrincipalManager)
        principal = principals.generate()
        
        user = models.UserPasswordAuthentication(username=id_token, 
                   principal_id=principal.getId())
        session.add(user)
        session.flush()
        return component.createObject(u'sparc.login.credential_identity', user.username)

    def get(self, identifier):
        """Return IIdentity provider for given identifier
        
        Args:
            identifier: String id_token, or IIdentified provider
        
        Raises:
            InvalidIdentification if identifier is not valid
        """
        user = self._get_model(identifier)
        return component.createObject(u'sparc.login.credential_identity', user.username)
    
    def contains(self, identifier):
        """True if identifier is assigned
        
        Args:
            identifier: String id_token, or IIdentified provider
        """
        session = component.getUtility(ISASession)
        return True if session.query(models.UserPasswordAuthentication).get(self._resolve(identifier)) else False
        
    def remove(self, identifier):
        """Remove identifier from manager
        
        Args:
            identifier: String id_token, or IIdentified provider
        
        Raises:
            InvalidIdentification if identifier is not valid
        """
        user = self._get_model(identifier)
        session = component.getUtility(ISASession)
        session.delete(user)
        session.flush()
    
    def discard(self, identifier):
        """Remove identifier from manager if available, otherwise does nothing
        
        Args:
            identifier: String id_token, or IIdentified provider
        """
        try:
            self.remove(identifier)
        except InvalidIdentification:
            pass
    
    def update(self, identifier, id_token):
        """Update and return ICredentialIdentity provider with new id_token
        
        Args:
            identifier: String id_token, or IIdentified provider
            id_token: new unique identifier String
        
        Raises:
            InvalidIdentification if identifier or id_token is not valid
        """
        user = self._get_model(identifier)
        if self.contains(id_token):
            raise InvalidIdentification('user already exists {}'.format(id_token))
        user.username = id_token
        component.getUtility(ISASession).flush()
        return component.createObject(u'sparc.login.credential_identity', user.username)
        