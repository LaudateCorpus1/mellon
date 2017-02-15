class MellonAPIAuthenticationException(Exception):
    """An exception related to authentication"""

class MellonAPIInvalidPassword(MellonAPIAuthenticationException):
    """Invalid password"""

class MellonAPIUserIsDisabled(MellonAPIAuthenticationException):
    """User is disabled"""