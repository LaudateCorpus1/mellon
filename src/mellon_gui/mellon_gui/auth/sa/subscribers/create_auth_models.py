from zope import component
from zope.interface.interfaces import IRegistrationEvent
from mellon_gui.sa import ISAEngine
from ..models import Base

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(ISAEngine, IRegistrationEvent)
def create_models(engine, event):
    Base.metadata.create_all(engine)