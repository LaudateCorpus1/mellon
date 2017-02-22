from zope import interface
from .. import IORMModel, ISAModel

# SECRET STATUS
class IORMSecretStatus(IORMModel):
    status_token = interface.Attribute("ASCII status token")

class ISASecretStatus(ISAModel, IORMSecretStatus):
    """A SA ORM secret status"""

# SECRET SEVERITY
class IORMSecretSeverity(IORMModel):
    severity_token = interface.Attribute("ASCII severity token")

class ISASecretSeverity(ISAModel, IORMSecretSeverity):
    """A SA ORM secret severity"""