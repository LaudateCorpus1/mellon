from zope import component
from zope import interface
import mellon

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(mellon.ISecretDiscoveredEvent)
def logger_reporter_for_secret(event):
    secret = event.object
    snippet = secret.__parent__
    mfile = snippet.__parent__
    logging.warn(\
                u"Found secret in file snippet.  Secret information: [{}]. Secret unique identifier [{}]. Snippet information: [{}].  File information: [{}].  Authorization context information [{}]"\
                .format(secret, secret.get_id(), snippet.__name__, mfile, mellon.IAuthorizationContext(snippet)))

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
