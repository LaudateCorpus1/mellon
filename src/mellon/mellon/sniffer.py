from zope import component
import zope.event
from . import IAuthorizationContext, ISnippetAvailableForSecretsSniffEvent, ISecretSniffer, IWhitelistChecker
from .events import SecretDiscoveredEvent

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(ISnippetAvailableForSecretsSniffEvent)
def global_secret_sniffer_processor(event):
    """Find all registered ISecretSniffer subscription adapters and process each one"""
    for sniffer in component.subscribers((event.object,), ISecretSniffer):
        for secret in sniffer:
            if component.getUtility(IWhitelistChecker).check(secret):
                logger.info(u"skipping white-listed secret: {}".format(secret))
                continue
            logger.debug(\
                u"Found secret in file snippet.  Notifying event.  Secret information: [{}]. Snippet information: [{}].  File information: [{}].  Authorization context information [{}]"\
                .format(secret, event.object.__name__, event.object.__parent__, IAuthorizationContext(event.object)))
            zope.event.notify(SecretDiscoveredEvent(secret))