from zope import interface

class IConfluenceMellonFile(interface.Interface):
    """Marker for confluence Mellon files"""

class IConfluenceSnippet(interface.Interface):
    """Marker for confluence snippets"""

class IConfluenceBytesSnippet(IConfluenceSnippet):
    """Marker for confluence bytes snippets"""

class IConfluenceUnicodeSnippet(IConfluenceSnippet):
    """Marker for confluence unicode snippets"""