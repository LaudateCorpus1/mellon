from datetime import datetime
from zope import component
import sqlalchemy
from sqlalchemy import orm
import mellon
from . import models

from sparc.logging import logging
logger = logging.getLogger(__name__)

_Commit = True # True indicates to issue a session commit for each reported secret
_Engine = None
_Session = None
_session = None
def _create_engine():
    m = mellon.mellon.get_registered_app()
    _dsn = m['vgetter'].get('SQLAlchemyORMReporter','SQLAlchemyReporter','SQLAlchemyEngine','dsn')
    _kwargs = m['vgetter'].get('SQLAlchemyORMReporter','SQLAlchemyReporter','SQLAlchemyEngine','kwargs', default={})
    if m['app'].debug:
        _kwargs['echo'] = True
    return sqlalchemy.create_engine(_dsn, **_kwargs)

def get_engine():
    """Return module SQLalchemy Engine singleton"""
    global _Engine
    if not _Engine:
        _Engine = _create_engine()
    return _Engine

def get_session():
    """Return SQLalchemy session object"""
    global _Session, _session
    if not _session:
        models.Base.metadata.create_all(get_engine())
        _Session = orm.sessionmaker(bind=get_engine())
        _session = _Session()
    return _session


@component.adapter(mellon.ISecretDiscoveredEvent)
def orm_reporter_for_secret(event):
    m = mellon.mellon.get_registered_app()
    now = datetime.now()
    if m['vgetter'].get('SQLAlchemyORMReporter', 'SQLAlchemyReporter', 
                                                    'utc_time', default=False):
        now = datetime.utcnow()
    session = get_session()
    #Create the ORM models, relationships, and merge them to session
    secret = event.object
    snippet = secret.__parent__
    mfile = snippet.__parent__
    auth_context =  mellon.IAuthorizationContext(mfile)
    #AuthorizationContext & MellonFile
    auth_context_model = None
    if auth_context.identity:
        auth_context_model = component.createObject(\
                    u"mellon_plugin.reporter.sqlalchemy.orm.model", 
                    mellon.IAuthorizationContext(mfile))
        auth_context_model = session.merge(auth_context_model)
    mfile_model = component.createObject(\
                    u"mellon_plugin.reporter.sqlalchemy.orm.model", mfile)
    mfile_model = session.merge(mfile_model)
    if auth_context_model:
        auth_context_model.mellon_files = [mfile_model]
    #Snippet
    snippet_model = session.query(models.Snippet).\
                    filter(
                            models.Snippet.name == str(snippet),
                            models.Snippet.mellon_file_name == mfile_model.name
                        ).first()
    if not snippet_model:
        snippet_model = component.createObject(\
                        u"mellon_plugin.reporter.sqlalchemy.orm.model", snippet)
    mfile_model.snippets = [snippet_model]
    session.flush()
    snippet_model = session.merge(snippet_model) #merges the id
    #Secret
    secret_model = session.query(models.Secret).\
                    filter(models.Secret.id == secret.get_id()).first()
    if not secret_model:
        secret_model = component.createObject(\
                    u"mellon_plugin.reporter.sqlalchemy.orm.model", secret)
    snippet_model.secrets = [secret_model]
    session.flush()
    #Discovery
    discovery_date_model = session.query(models.SecretDiscoveryDate).\
                    filter(models.SecretDiscoveryDate.secret_id == secret_model.id,
                           models.SecretDiscoveryDate.datetime == now)\
                    .first()
    if not discovery_date_model:
        discovery_date_model = models.SecretDiscoveryDate(datetime=now)
    secret_model.secret_discovery_dates = [discovery_date_model]
    session.flush()
    if _Commit:
        session.commit()
    logger.debug(\
                u"Secret persisted to ORM storage.  Secret information: [{}]. Secret unique identifier [{}]. Snippet information: [{}].  File information: [{}].  Authorization context information [{}]"\
                .format(secret, secret.get_id(), snippet.__name__, mfile, mellon.IAuthorizationContext(snippet)))
