from zope import component
from zope import interface
import mellon

CALLED_BYTES = False
CALLED_UNICODE = False

def reset_test_sniffer():
    global CALLED_BYTES, CALLED_UNICODE
    CALLED_BYTES = CALLED_UNICODE = False

@interface.implementer(mellon.ISecretSniffer)
@component.adapter(mellon.IBytesSnippet)
class TestBytesSecretSniffer(object):
    def __init__(self, context):
        self.context = context
    
    def __iter__(self):
        global CALLED_BYTES
        if not CALLED_BYTES:
            yield component.createObject(u"mellon.secret", 
                            name=u"This is a test bytes secret", parent=self.context)
            CALLED_BYTES = True

@interface.implementer(mellon.ISecretSniffer)
@component.adapter(mellon.IUnicodeSnippet)
class TestUnicodeSecretSniffer(object):
    def __init__(self, context):
        self.context = context
    
    def __iter__(self):
        global CALLED_UNICODE
        if not CALLED_UNICODE:
            yield component.createObject(u"mellon.secret", 
                            name=u"This is a test unicode secret", parent=self.context)
            CALLED_UNICODE = True
