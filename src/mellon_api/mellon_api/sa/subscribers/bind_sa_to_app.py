from zope import component
from zope import interface
from zope.interface.interfaces import IRegistrationEvent
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import mellon_api
from mellon_api.sa import ISAEngine, ISASession
from mellon_plugin.reporter.sqlalchemy import orm
from ..models import Base

@component.adapter(mellon_api.IFlaskApplication, IRegistrationEvent)
def create_and_register_sa_utils(app, event):
    sm = component.getSiteManager()
    if not sm.queryUtility(ISAEngine):
        engine = orm.db.create_engine()
        interface.alsoProvides(engine, ISAEngine)
        sm.registerUtility(engine, ISAEngine)
    
    if not sm.queryUtility(ISASession):
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory) #thread-local sessions
        interface.alsoProvides(Session, ISASession)
        sm.registerUtility(Session, ISASession) # call component.getUtility(ISASession) to get thread-local session

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
        if not exception:
            component.getUtility(ISASession).commit()
        component.getUtility(ISASession).remove()
    _test_commit_request_registrations = True