from zope import component
from zope import interface
from eve import Eve
from sparc.configuration.container import application
import mellon
import mellon_api
from mellon import IMellonApplication
from mellon.mellon import create_and_register_app, get_registered_app

DESCRIPTION="""\
Mellon Restful API server.
"""

@interface.implementer(mellon_api.IEveApplicationKwargs)
class EveApplicationKwargs(object):
    def __init__(self):
        self.kwargs = {}

def create_eve_app():
    m = get_registered_app()
    config_settings = m['vgetter'].get('Eve', default={})
    
    kwargs = component.getUtility(mellon_api.IEveApplicationKwargs).kwargs
    if 'settings' not in kwargs:
        kwargs['settings'] = {}
    if 'DOMAIN' not in kwargs['settings']:
        kwargs['settings']['DOMAIN'] = {}
    config_settings.update(kwargs['settings']) #over-write conflicting keys
    kwargs['settings'] = config_settings
    eve_app = Eve(**kwargs)
    interface.alsoProvides(eve_app, mellon_api.IEveApplication)
    return eve_app

def create_and_register_eve_app():
    eve_app = create_eve_app()
    sm = component.getSiteManager()
    sm.registerUtility(eve_app, mellon_api.IEveApplication) #give components access to app config

def main():
    args = application.getScriptArgumentParser(DESCRIPTION).parse_args()
    # we'll override the core ZCML initializer with our own. then create the
    # base mellon application and init the component registry with the 
    # yaml-based zcml entry points
    mellon.mellon.Mellon.app_zcml = (mellon_api, 'configure.zcml')
    create_and_register_app(args.config_file, args.verbose, args.debug)
    component.getUtility(IMellonApplication).configure()
    #create, register, and run the Eve application
    create_and_register_eve_app()
    component.getUtility(mellon_api.IEveApplication).run()

if __name__ == '__main__':
    main()