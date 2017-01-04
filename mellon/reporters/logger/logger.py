from zope import component
from zope import interface
import mellon

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(mellon.ISnippetAvailableForSecretsSniffEvent)
def logger_reporter_for_secret_sniffers(event):
    for sniffer in component.subscribers((event.object,), mellon.ISecretSniffer):
        for secret in sniffer:
            if component.getUtility(mellon.IWhitelistChecker).check(secret):
                logger.info(u"skipping white-listed secret: {}".format(secret))
                continue
            logging.warn(\
                u"Found secret in file snippet.  Secret information: [{}]. Snippet information: [{}].  File information: [{}]."\
                .format(secret, event.object.__name__, event.object.__parent__))

@interface.implementer(mellon.ISecret)
class TestSecret(object):
    def __init__(self, name, parent):
        self.__name__ = name
        self.__parent__ = parent
    def __str__(self):
        return self.__name__

@interface.implementer(mellon.ISecretSniffer)
@component.adapter(mellon.ISnippet)
class TestSecretSniffer(object):
    def __init__(self, context):
        self.context = context
    
    def __call__(self):
        return TestSecret(name=u"This is a test secret", parent=self.context)
