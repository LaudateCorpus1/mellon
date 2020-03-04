from zope import component
from mellon.exceptions import MellonConfigurationError
from mellon.mellon import get_registered_app
from pyramid.interfaces import IAuthenticationPolicy, IApplicationCreated
from ..ticket import UserPasswordAuthenticationManagerTktPolicy

@component.adapter(IApplicationCreated)
def register_ticket_authn_policy(created):
    vgetter = get_registered_app()['vgetter']
    options = vgetter.get_value('PyramidAuthTktAuthenticationPolicy', default={})
    if not options.get('secret', None):
        raise MellonConfigurationError("Expected Mellon configuration entry for PyramidAuthTktAuthenticationPolicy:secret")
    authn_policy = UserPasswordAuthenticationManagerTktPolicy(**options)
    created.app.registry.registerUtility(authn_policy, IAuthenticationPolicy)