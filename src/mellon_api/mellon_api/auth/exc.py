class MellonAPIAuthenticationException(Exception):
    """An exception related to authentication"""

class MellonAPIInvalidPassword(MellonAPIAuthenticationException):
    """Invalid password"""

class MellonAPIUserIsDisabled(MellonAPIAuthenticationException):
    """User is disabled"""
    
class MellonAPITokenIsExpired(MellonAPIAuthenticationException):
    """Token is expired"""

class MellonAPIInvalidTokenSignature(MellonAPIAuthenticationException):
    """Invalid token signature"""