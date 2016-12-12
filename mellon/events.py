from zope import interface
from zope.interface.interfaces import ObjectEvent
from .interfaces import ISnippetAvailableForSecretsSniffEvent

@interface.implementer(ISnippetAvailableForSecretsSniffEvent)
class SnippetAvailableForSecretsSniffEvent(ObjectEvent):
    pass