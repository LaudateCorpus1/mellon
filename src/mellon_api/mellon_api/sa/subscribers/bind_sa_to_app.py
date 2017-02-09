from zope import component
from zope import interface
from zope.interface.interfaces import IRegistrationEvent
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import mellon_api
from mellon_api.sa import ISAEngine, ISASession
from mellon_plugin.reporter.sqlalchemy.orm import db
from ..models import Base

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(mellon_api.IFlaskApplication, IRegistrationEvent)
def create_and_register_sa_utils(app, event):
    sm = component.getSiteManager()
    engine = sm.queryUtility(ISAEngine)
    if not engine:
        engine = db.create_engine()
        interface.alsoProvides(engine, ISAEngine)
        sm.registerUtility(engine, ISAEngine)
        logger.debug("registered ISAEngine based on mellon_api yaml config for SQLAlchemyORMReporter key")
    else:
        logger.debug("ISAEngine engine already available, no need to create and register a new one.")
    
    if not sm.queryUtility(ISASession):
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory) #thread-local sessions
        interface.alsoProvides(Session, ISASession)
        sm.registerUtility(Session, ISASession) # call component.getUtility(ISASession) to get thread-local session
        logger.debug("registered scoped ISASession session utility based")
    else:
        logger.debug("ISASession engine already available, no need to create and register a new one.")

@component.adapter(ISAEngine, IRegistrationEvent)
def create_models(engine, event):
    Base.metadata.create_all(engine)

# hackish way to test for registrations
_test_commit_request_registrations = False
@component.adapter(ISASession, IRegistrationEvent)
def commit_request(session, event):
    global _test_commit_request_registrations
    app = component.getUtility(mellon_api.IFlaskApplication)
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if component.queryUtility(ISASession):
            if not exception:
                component.getUtility(ISASession).commit()
            component.getUtility(ISASession).remove()
        else:
            logger.warn("expected to find a ISASession in order to commit and remove session data, but could not.  The ISASession was probably removed out of band.")
    _test_commit_request_registrations = True