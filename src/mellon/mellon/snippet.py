from zope.component.factory import Factory
from zope import interface
from zope.schema._compat import make_binary
from . import IBytesSnippet
from . import IUnicodeSnippet

@interface.implementer(IBytesSnippet)
class BytesSnippet(object):
    
    def __init__(self, snippet=b'', name=None, parent=None):
        self.data = make_binary(snippet)
        #zope.location.ILocation
        self.__name__ = name
        self.__parent__ = parent
bytesSnippetFactory = Factory(BytesSnippet)

@interface.implementer(IUnicodeSnippet)
class UnicodeSnippet(object):
    
    def __init__(self, snippet=u'', name=None, parent=None):
        self.data = snippet
        #zope.location.ILocation
        self.__name__ = name
        self.__parent__ = parent
unicodeSnippetFactory = Factory(UnicodeSnippet)