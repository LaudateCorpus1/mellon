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