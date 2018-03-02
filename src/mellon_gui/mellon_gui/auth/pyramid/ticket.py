from zope import component
from zope import interface
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Everyone, Authenticated
from sparc.login.credentials import ICredentialIdentityManager
from sparc.login.principal import IPrincipal, IPrincipalManager
from .principals import MellonReaderRole, MellonWriterRole

@interface.implementer(IAuthenticationPolicy)
class UserPasswordAuthenticationManagerTktPolicy(AuthTktAuthenticationPolicy):
    """Ticket manager extenion that enforces removed principals and assigns 
        Mellon gui roles to all authenticated users
    """
    def authenticated_userid(self, request):
        manager = component.getUtility(ICredentialIdentityManager)
        credential_id = self.unauthenticated_userid(request)
        if credential_id:
            if manager.contains(credential_id):
                return credential_id

    def effective_principals(self, request):
        manager = component.getUtility(IPrincipalManager)
        principals = [Everyone]
        credential_id = self.authenticated_userid(request)
        if manager.contains(credential_id):
            principal = IPrincipal(manager.get(credential_id))
            principals += [Authenticated, MellonReaderRole, MellonWriterRole, str(principal.getId())]
        return principals
