from zope import component
from zope import interface
from zope.interface.interfaces import IRegistrationEvent
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from pyramid.interfaces import IApplicationCreated
from pyramid.threadlocal import get_current_registry
from .. import ISAEngine, ISASession
from mellon import IMellonApplication
from mellon_plugin.reporter.sqlalchemy.orm import db
from ..models import Base

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(IApplicationCreated)
def create_and_register_sa_utils(app):
    """Establish SA engine/session into Pyramid transaction machinery
    
    see http://docs.pylonsproject.org/projects/pyramid/en/latest/quick_tutorial/databases.html
    """
    sm = get_current_registry()
    engine = sm.queryUtility(ISAEngine)
    if not engine:
        engine = db.get_engine()
        interface.alsoProvides(engine, ISAEngine)
        sm.registerUtility(engine, ISAEngine)
        logger.debug("registered ISAEngine based on mellon_gui yaml config for SQLAlchemyORMReporter key")
    else:
        logger.debug("ISAEngine engine already available, no need to create and register a new one.")
    
    if not sm.queryUtility(ISASession):
        session_factory = sessionmaker(extension=ZopeTransactionExtension()) #integrate with Pyramid transaction machinery
        Session = scoped_session(session_factory) #thread-local sessions
        Session.configure(bind=engine)
        interface.alsoProvides(Session, ISASession)
        sm.registerUtility(Session, ISASession) # call component.getUtility(ISASession) to get thread-local session
        logger.debug("registered scoped ISASession session utility based")
    else:
        logger.debug("ISASession engine already available, no need to create and register a new one.")

