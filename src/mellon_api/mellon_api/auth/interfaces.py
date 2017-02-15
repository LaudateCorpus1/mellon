from zope import interface
from mellon_plugin.reporter.sqlalchemy.orm import IORMModel, ISAModel

# PRINCIPAL
class IORMPrincipal(IORMModel):
    """Principal tokens"""
    id = interface.Attribute("Integer unique principal token")
class ISAPrincipal(ISAModel, IORMPrincipal):
    """A SA ORM principal"""

# USER LOGIN
class IORMUserPasswordAuthentication(IORMModel):
    """Standard login authentication data"""
    username = interface.Attribute("Unicode unique username")
    password_crypt = interface.Attribute("Unicode unique username")
    principal_id = interface.Attribute("Integer related principal token")
class ISAUserPasswordAuthentication(ISAModel, IORMUserPasswordAuthentication):
    """A SA ORM UserPasswordAuthentication"""

class ICryptContext(interface.Interface):
    """Marker for a passlib.context.CryptContext object"""

class IUserPasswordAuthenticationManager(interface.Interface):
    """Manage user password authentication entries"""
    def create(username, password, principal_id=None):
        """Create a new user authentication entry
        
        Args:
            username: Unicode unique username
            password: Unicode plain-text password
            principal_id: associate username with given principal.  defaults to 
                          new principal generation.
        Returns:
            IORMUserPasswordAuthentication provider
        """
    
    def check_authentication(username, password):
        """Raises exc.MellonAPIAuthenticationException for invalid combinations"""
    
    def update_password(username, password):
        """Updates username with new password."""
    
    def update_username(username, new):
        """Updates username with new."""
    
    def disable(username):
        """Sets the password entry to null for username, effectively disabling authentication ability"""
    
    def delete(username):
        """Deletes username (does not remove related principal)"""

class IAuthenticationProvider(interface.Interface):
    """Provides a mechanism to authenticate"""
    def __call__():
        """Raises flask_restless.ProcessingException on authentication failure"""