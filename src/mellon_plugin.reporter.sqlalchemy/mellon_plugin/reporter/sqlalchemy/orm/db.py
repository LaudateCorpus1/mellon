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
    secret = event.object
    snippet = secret.__parent__
    mfile = snippet.__parent__
    session = get_session()
    
    ormSecContext = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.model", mellon.IAuthorizationContext(mfile))
    session.merge(ormSecContext)
    ormFile = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.model", mfile)
    session.merge(ormFile)
    ormSnippet = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.model", snippet)
    session.merge(ormSnippet)
    if not ormSnippet.id:
        session.add(ormSnippet)
        session.flush()
    ormSecret = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.model", secret, secret_snippet_id=ormSnippet.id)
    session.merge(ormSecret)
    session.commit()
    
    logger.debug(\
                u"Found secret in file snippet.  Secret information: [{}]. Secret unique identifier [{}]. Snippet information: [{}].  File information: [{}].  Authorization context information [{}]"\
                .format(secret, secret.get_id(), snippet.__name__, mfile, mellon.IAuthorizationContext(snippet)))
