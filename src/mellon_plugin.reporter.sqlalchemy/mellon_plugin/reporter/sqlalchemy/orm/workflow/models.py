from zope import interface
import sqlalchemy
from . import interfaces
from ..models import Base, Secret


@interface.implementer(interfaces.ISASecretStatus)
class SecretStatus(Base):
    __tablename__ = 'workflow_secret_status'
    __table_args__ = (sqlalchemy.PrimaryKeyConstraint(\
                    'token', 'secret_id', name='secret_status_pk'),)
    token = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    secret_id = sqlalchemy.Column(sqlalchemy.String, 
                    sqlalchemy.ForeignKey(Secret.__tablename__ + '.id'),
                    nullable=False)

@interface.implementer(interfaces.ISASecretSeverity)
class SecretSeverity(Base):
    __tablename__ = 'workflow_secret_severity'
    __table_args__ = (sqlalchemy.PrimaryKeyConstraint(\
                    'token', 'secret_id', name='secret_severity_pk'),)
    token = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    secret_id = sqlalchemy.Column(sqlalchemy.String, 
                    sqlalchemy.ForeignKey(Secret.__tablename__ + '.id'),
                    nullable=False)