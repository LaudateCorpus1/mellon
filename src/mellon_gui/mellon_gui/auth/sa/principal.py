from zope import component
from zope import interface

from sparc.login.principal import IPrincipalManager
from sparc.login.identification import IIdentified
from sparc.login.identification.exceptions import InvalidIdentification
from mellon_gui.sa import ISASession
from . import models

@interface.implementer(IPrincipalManager)
class SessionPrincipalManager(object):
    
    def _resolve(self, identifier):
        return identifier.getId() if IIdentified.providedBy(identifier) else identifier
    
    def _get_model(self, identifier):
        session = component.getUtility(ISASession)
        principal = session.query(models.Principal).get(self._resolve(identifier))
        if not principal:
            raise InvalidIdentification("specified principal does not exist {}".format(identifier))
        return principal
    
    def generate(self, hint=None):
        """Generates and returns a new IIdentity provider
        
        Args:
            hint: String hint to base new identity on.  Implementers may ignore
                  this argument.
        """
        session = component.getUtility(ISASession)
        principal = models.Principal()
        session.add(principal)
        session.flush() #generates the principal id
        return component.createObject(u'sparc.login.principal', principal.id)
        
    def create(self, id_token):
        """Creates and returns a new IIdentity provider
        
        Args:
            id_token: Assign identifier String as unique identifier.
        
        Raises:
            InvalidIdentification if identifier is not valid
        """
        raise InvalidIdentification('implementation does not allow for specified token creation, use generate() instead.')
    
    def get(self, identifier):
        """Return IIdentity provider for given identifier
        
        Args:
            identifier: String id_token, or IIdentified provider
        
        Raises:
            InvalidIdentification if identifier is not valid
        """
        return component.createObject(u'sparc.login.principal', self._get_model(identifier).id)
    
    def contains(self, identifier):
        """True if identifier is assigned
        
        Args:
            identifier: String id_token, or IIdentified provider
        """
        session = component.getUtility(ISASession)
        return True if session.query(models.Principal).get(self._resolve(identifier)) else False
        
    def remove(self, identifier):
        """Remove identifier from manager
        
        Args:
            identifier: String id_token, or IIdentified provider
        
        Raises:
            InvalidIdentification if identifier is not valid
        """
        principal = self._get_model(identifier)
        session = component.getUtility(ISASession)
        session.delete(principal)
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