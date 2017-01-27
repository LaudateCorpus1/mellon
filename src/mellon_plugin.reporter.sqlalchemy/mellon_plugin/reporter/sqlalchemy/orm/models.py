import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from zope.component.factory import Factory
from zope import interface
from . import interfaces
import mellon

Base = declarative_base()

@interface.implementer(interfaces.ISAModel)
class OrmModelFromMellonProvider(object):
    def __new__(self, mellon_provider, secret_snippet_id=None):
        """Return a valid model object from a mellon object
        
        behavior is undefined for mellon_provider providing more than one valid
        interface.
        
        Returned objects are not SA session aware.  This is a simple convenience
        factory to generate SA models from Mellon interface providers.
        
        Args:
            mellon_provider: Object providing one of the following from mellon: 
                             IAuthorizationContext, IMellonFile, ISnippet, 
                             or ISecret
            secret_snippet_id: if mellon_provider is a new ISecret provider, then
                               you must provide the valid foreign key id for
                               the related IORMSnippet provider.  This
                               information is not available within the 
                               mellon.ISecret provider path
        Returns:
            A valid SQLAlchemy ORM object providing the corresponding ISAxxx
            interface where xxx is Secret, Snippet, MellonFile, etc.
        """
        obj = None
        if mellon.IAuthorizationContext.providedBy(mellon_provider):
            obj = AuthorizationContext()
            obj.id = mellon_provider.identity
            obj.name = str(mellon_provider)
            obj.description = mellon_provider.description
        elif mellon.IMellonFile.providedBy(mellon_provider):
            obj = MellonFile()
            obj.name = str(mellon_provider)
            obj.authorization_context_id = mellon.IAuthorizationContext(mellon_provider).identity
        elif mellon.ISnippet.providedBy(mellon_provider):
            obj = Snippet()
            obj.name = mellon_provider.__name__
            if mellon.IBytesSnippet.providedBy(mellon_provider):
                obj.data_blob = mellon_provider.data
            else:
                obj.data_text = mellon_provider.data
            obj.mellon_file_name = str(mellon_provider.__parent__)
        elif mellon.ISecret.providedBy(mellon_provider):
            obj = Secret()
            obj.id = mellon_provider.get_id()
            obj.name = str(mellon_provider)
            obj.snippet_id = secret_snippet_id
        if not obj:
            raise ValueError("expected mellon_provider argument to provide a valid Mellon interface {}".format(mellon_provider))
        return obj
ormModelFromMellonProviderFactory = Factory(OrmModelFromMellonProvider)

@interface.implementer(interfaces.ISAAuthorizationContext)
class AuthorizationContext(Base):
    __tablename__ = 'authorization_contexts'
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    description = sqlalchemy.Column(sqlalchemy.String)
    mellon_files = orm.relationship('MellonFile', 
                                                     back_populates='authorization_context')

@interface.implementer(interfaces.ISAMellonFile)
class MellonFile(Base):
    __tablename__ = 'mellon_files'
    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    authorization_context_id = \
                sqlalchemy.Column(sqlalchemy.String, 
                    sqlalchemy.ForeignKey(\
                                    AuthorizationContext.__tablename__ + '.id'),
                    nullable=True) #not all files will have a security context
    authorization_context = orm.relationship('AuthorizationContext', 
                                             back_populates=__tablename__)
    snippets = orm.relationship('Snippet', back_populates='mellon_file')

@interface.implementer(interfaces.ISASnippet)
class Snippet(Base):
    __tablename__ = 'snippets'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    data_blob = sqlalchemy.Column(sqlalchemy.BLOB)
    data_text = sqlalchemy.Column(sqlalchemy.Text)
    mellon_file_name = sqlalchemy.Column(sqlalchemy.String, 
                    sqlalchemy.ForeignKey(MellonFile.__tablename__ + '.name'),
                    nullable=False)
    mellon_file = orm.relationship('MellonFile', back_populates=__tablename__)
    secrets = orm.relationship('Secret', back_populates='snippet')

@interface.implementer(interfaces.ISASecret)
class Secret(Base):
    __tablename__ = 'secrets'
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    snippet_id = sqlalchemy.Column(sqlalchemy.String, 
                    sqlalchemy.ForeignKey(Snippet.__tablename__ + '.id'),
                    nullable=False)
    snippet = orm.relationship('Snippet', back_populates=__tablename__)

