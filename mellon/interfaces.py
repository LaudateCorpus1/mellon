from zope import component
from zope import interface
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface.interfaces import IObjectEvent
from zope import location
from sparc.configuration.container import ISparcPyContainerConfiguredApplication

#EVENTS
class ISnippetAvailableForSecretsSniffEvent(IObjectEvent):
    """An object providing ISnippet is ready to be sniffed for secrets"""
class ISecretDiscoveredEvent(IObjectEvent):
    """An object providing ISecret has been discovered"""

#APPLICATION & FACTORIES
class IMellonApplication(ISparcPyContainerConfiguredApplication):
    """The Application"""

class IMellonFileProvider(interface.Interface):
    """Provides IFile objects that should be processed by the application"""
    def __iter__():
        """Iterator of IFile objects"""

class IMellonFileProviderFactory(component.IFactory):
    """A factory producing a IMellonFileProvider"""
    def __call__(config):
        """
        Args:
            config; factory specific data structure holding required object
                    initialization information needed by factory
        """

#SNIPPETS
class ISnippet(location.ILocation):
    """A snippet of data to be sniffed for secrets
    
    This also implements ILocation, where __parent__ is a IMellonFile and
    __name__ indicates where in the file the snippet can be located at.
    """
    data = interface.Attribute("A Python data sequence")

class IBytesSnippet(ISnippet):
    """A snippet of bytes data to be sniffed for secrets"""
    data = interface.Attribute("A Python bytes sequence")

class IUnicodeSnippet(ISnippet):
    """A snippet of unicode data to be sniffed for secrets"""
    data = interface.Attribute("A Python unicode sequence")
        
class ISnippetIterator(interface.Interface):
    """Iterates data snippets"""
    def __iter__():
        """Iterator of ISnippet objects"""

#FILES
class IPath(interface.Interface):
    """Marker for text that is a formatted file system path"""
class IFile(interface.Interface):
    """Marker for file-like object providing Python's file object interface"""

class IMellonFile(ISnippetIterator, IAttributeAnnotatable):
    """A file to be processed by the application"""
    def __str__():
        """String locatable identity of file"""

class IUnicodeMellonFile(IMellonFile):
    """A Unicode (text) file to be processed by the application"""
    snippet_lines_increment = \
        interface.Attribute("Number of lines to jump after each snippet, 0 "+
                            "indicates entire data.")
    snippet_lines_coverage = \
        interface.Attribute("Number of lines to include in each snippet "+
                            "if available, 0 indicates all remaining lines.")

class IByteMellonFile(IMellonFile):
    """A byte (binary) file to be processed by the application"""
    read_size = interface.Attribute(\
        "Max number of bytes to include in each file read operation."+
        "Number of bytes to jump after each snippet, 0 indicates entire data.")
    snippet_bytes_increment = \
        interface.Attribute("Number of read_size data packets to jump after "+
                            "snippet return.")
    snippet_bytes_coverage = \
        interface.Attribute("Number of read_size data packets to include in "+
                            "each snippet. 0 indicates all data packets.")

class IBinaryChecker(interface.Interface):
    """Binary file checker"""
    def check():
        """True indicates the data was found to be binary"""

# SNIFFERS, SECRETS, WHITELISTS
class ISecretSniffer(interface.Interface):
    """Looks for a secret"""
    def __iter__():
        """Iterator of found ISecret providers"""

class ISecret(location.ILocation):
    """A secret found within a ISnippet
    
    This also implements ILocation, where __parent__ is a ISnippet and
    __name__ is alias for __str__.
    """
    def __str__():
        """String details of the secret and/or how it was found"""
    
    def __hash__():
        """Uniquely identifies the locatable secret among other secrets"""

class IWhitelistInfo(interface.Interface):
    """Object whitelist information"""
    def __str__():
        """Detailed information on how object was whitelisted"""

class IWhitelist(interface.Interface):
    """Identifies if object is whitelisted"""
    def __iter__():
        """Iterator of found IWhitelistInfo providers"""

class IWhitelistChecker(interface.Interface):
    """Object whitelist checker"""
    def check(item):
        """True if item is whitelisted in any registered IWhitelist provider"""

# SECURITY
class IAuthorizationContext(interface.Interface):
    """Information about contextual identity."""
    identity = interface.Attribute("Text identity")
    description = interface.Attribute("Text context describer")
    
    def __str__(self):
        """String representation of authorization context"""

class IApplyAuthorizationContext(interface.Interface):
    def __call__(context, item):
        """Apply a security context to a item
        
        Args:
            context: IAuthorizationContext provider
            item: item that is adaptable into a IAuthorizationContext provider
        
        Returns:
            IAuthorizationContext provider for item with context's attributes applied
        """