from zope import component
from zope import interface
import mellon

CALLED_BYTES = False
CALLED_UNICODE = False

@interface.implementer(mellon.ISecretSniffer)
@component.adapter(mellon.IBytesSnippet)
class TestBytesSecretSniffer(object):
    def __init__(self, context):
        self.context = context
    
    def __call__(self):
        global CALLED_BYTES
        return_ = None
        if not CALLED_BYTES:
            return_ = component.createObject(u"mellon.secret", 
                            name=u"This is a test bytes secret", parent=self.context)
            CALLED_BYTES = True
        return return_

@interface.implementer(mellon.ISecretSniffer)
@component.adapter(mellon.IUnicodeSnippet)
class TestUnicodeSecretSniffer(object):
    def __init__(self, context):
        self.context = context
    
    def __call__(self):
        global CALLED_UNICODE
        return_ = None
        if not CALLED_UNICODE:
            return_ = component.createObject(u"mellon.secret", 
                            name=u"This is a test unicode secret", parent=self.context)
            CALLED_UNICODE = True
        return return_