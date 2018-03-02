from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.registry import Registry
from zope.component import getGlobalSiteManager
from zope import component
from mellon import mellon
import mellon_gui
from .events import PyramidConfigInitialized
from .views import sb_admin_v2

def populate_pyramid_config(config):
    config.include('pyramid_tm') #transaction manager (SQL Alchemeny)
    config.include('pyramid_chameleon')
    config.include('pyramid_zcml')
    config.load_zcml('mellon_gui:configure.zcml')
    
    #check for an authentication policy
    authn_policy = component.queryUtility(IAuthenticationPolicy)
    if authn_policy:
        config.set_authentication_policy(authn_policy)
        config.set_authorization_policy(ACLAuthorizationPolicy())

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    
    see http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/zca.html#zca-chapter
    We use the 'Enabling the ZCA global API by using the ZCA global registry'
    option to give direct access to Mellon components via the standard Zope
    Component API calls.
    """
    #init the ZCA registry with Mellon components
    mellon_verbose = True if settings.get('mellon.verbose', '').lower() == 'true' else False
    mellon_debug = True if settings.get('mellon.debug', '').lower() == 'true' else False
    mellon_app = mellon.create_app(settings['mellon.config'], mellon_verbose, mellon_debug)
    mellon_app.configure() # sets up subscribers (and other stuff)
    mellon.register_app(mellon_app) # sends hookable registration event
    
    #create the pyramid app, while passing in the populated global registry from above
    globalreg = getGlobalSiteManager()
    config = Configurator(registry=globalreg)
    config.setup_registry(settings=settings)
    populate_pyramid_config(config)
    config.registry.notify(PyramidConfigInitialized(config))
    
    #map the sb-admin-v2 theme dir to root as a catch-all.  This makes for
    #easier copy/paste template building based off of theme mock-up samples
    config.add_route('catchall_static', '/*subpath')
    config.add_view(sb_admin_v2, route_name='catchall_static')
    
    return config.make_wsgi_app()
