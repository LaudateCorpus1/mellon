from zope import interface
from zope.interface.interfaces import ObjectEvent
from .interfaces import ISecretDiscoveredEvent, ISnippetAvailableForSecretsSniffEvent

@interface.implementer(ISnippetAvailableForSecretsSniffEvent)
class SnippetAvailableForSecretsSniffEvent(ObjectEvent):
    pass

@interface.implementer(ISecretDiscoveredEvent)
class SecretDiscoveredEvent(ObjectEvent):
    pass