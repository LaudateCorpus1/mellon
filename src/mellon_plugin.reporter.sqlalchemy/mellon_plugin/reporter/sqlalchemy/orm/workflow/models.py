from zope import interface
import sqlalchemy
from . import interfaces
from ..models import Secret

Secret.status_token = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='')
interface.classImplements(Secret, interfaces.ISASecretStatus)

Secret.severity_token = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='')
interface.classImplements(Secret, interfaces.ISASecretSeverity)
