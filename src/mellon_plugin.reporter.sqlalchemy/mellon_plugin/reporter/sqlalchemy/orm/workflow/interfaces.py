from zope import interface
from .. import IORMModel, ISAModel

# SECRET STATUS
class IORMSecretStatus(IORMModel):
    status = interface.Attribute("ASCII status token")
    secret_id = interface.Attribute("Valid IORMSecret.id reference")

class ISASecretStatus(ISAModel, IORMSecretStatus):
    """A SA ORM secret status"""

# SECRET SEVERITY
class IORMSecretSeverity(IORMModel):
    severity = interface.Attribute("ASCII severity token")
    secret_id = interface.Attribute("Valid IORMSecret.id reference")

class ISASecretSeverity(ISAModel, IORMSecretSeverity):
    """A SA ORM secret severity"""