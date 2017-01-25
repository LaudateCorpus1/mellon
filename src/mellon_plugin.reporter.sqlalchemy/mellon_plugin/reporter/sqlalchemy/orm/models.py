import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AuthorizationContext(Base):
    __tablename__ = 'authorization_contexts'
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    description = sqlalchemy.Column(sqlalchemy.String)

class MellonFile(Base):
    __tablename__ = 'mellon_files'
    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    authorization_context_id = sqlalchemy.Column(sqlalchemy.String, 
                    sqlalchemy.ForeignKey(\
                                    AuthorizationContext.__tablename__ + '.id'),
                    nullable=False)
    authorization_context = orm.relationship('AuthorizationContext', 
                                             back_populates=__tablename__)
AuthorizationContext.mellon_files = orm.relationship('MellonFile', 
                                                     back_populates='authorization_context')

class Snippet(Base):
    __tablename__ = 'snippets'
    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    data_blob = sqlalchemy.Column(sqlalchemy.BLOB)
    data_text = sqlalchemy.Column(sqlalchemy.Text)
    mellon_file_name = sqlalchemy.Column(sqlalchemy.String, 
                    sqlalchemy.ForeignKey(MellonFile.__tablename__ + '.name'),
                    nullable=False)
    mellon_file = orm.relationship('MellonFile', back_populates=__tablename__)
MellonFile.snippets = orm.relationship('Snippet', back_populates='mellon_file')

class Secret(Base):
    __tablename__ = 'secrets'
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    snippet_name = sqlalchemy.Column(sqlalchemy.String, 
                    sqlalchemy.ForeignKey(Snippet.__tablename__ + '.name'),
                    nullable=False)
    snippet = orm.relationship('Snippet', back_populates=__tablename__)
Snippet.secrets = orm.relationship('Secret', back_populates='snippet')
