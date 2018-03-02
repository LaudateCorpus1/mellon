class MellonGuiAuthAuthenticationException(Exception):
    """An exception related to authentication"""

class MellonGuiAuthInvalidPassword(MellonGuiAuthAuthenticationException):
    """Invalid password"""

class MellonGuiAuthUserIsDisabled(MellonGuiAuthAuthenticationException):
    """User is disabled"""
    
class MellonGuiAuthTokenIsExpired(MellonGuiAuthAuthenticationException):
    """Token is expired"""

class MellonGuiAuthInvalidTokenSignature(MellonGuiAuthAuthenticationException):
    """Invalid token signature"""