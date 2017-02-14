from zope import interface
import sqlalchemy
from mellon_plugin.reporter.sqlalchemy.orm.models import Base
from . import interfaces

@interface.implementer(interfaces.ISAPrincipal)
class Principal(Base):
    __tablename__ = 'principals'
    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)


@interface.implementer(interfaces.ISAUserPasswordAuthentication)
class UserPasswordAuthentication(Base):
    __tablename__ = 'user_password_authentication'
    username = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False, primary_key=True)
    password_crypt = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    principal_id = \
                sqlalchemy.Column(sqlalchemy.Integer, 
                    sqlalchemy.ForeignKey(\
                                    Principal.__tablename__ + '.id'),
                    nullable=False)