from datetime import datetime
from zope import component
import sqlalchemy
from sqlalchemy import orm
import mellon
from . import models

from sparc.logging import logging
logger = logging.getLogger(__name__)

_Engine = None
_Session = None
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
    global _Session
    if not _Session:
        models.Base.metadata.create_all(get_engine())
        _Session = orm.sessionmaker(bind=get_engine())
    return _Session()


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
        session.add(auth_context_model)
    mfile_model = component.createObject(\
                    u"mellon_plugin.reporter.sqlalchemy.orm.model", mfile)
    if auth_context_model:
        auth_context_model.mellon_files = [mfile_model]
    session.add(mfile_model)
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
        session.add(snippet_model) #add makes a diference vs merge for autoincrement id generation
    #Secret
    secret_model = component.createObject(\
                    u"mellon_plugin.reporter.sqlalchemy.orm.model", secret)
    snippet_model.secrets = [secret_model]
    session.add(snippet_model)
    discovery_date_model = models.SecretDiscoveryDate(datetime=now)
    secret_model.secret_discovery_dates = [discovery_date_model]
    session.add(discovery_date_model)
    

    session.commit()
    logger.debug(\
                u"Secret persisted to ORM storage.  Secret information: [{}]. Secret unique identifier [{}]. Snippet information: [{}].  File information: [{}].  Authorization context information [{}]"\
                .format(secret, secret.get_id(), snippet.__name__, mfile, mellon.IAuthorizationContext(snippet)))
