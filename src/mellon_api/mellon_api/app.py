from zope import component
from zope import interface
from flask import Flask
from sparc.configuration.container import application
import mellon
import mellon_api
from mellon import IMellonApplication
from mellon.mellon import create_and_register_app, get_registered_app

DESCRIPTION="""\
Mellon Restful API server.
"""


def create_flask_app():
    return Flask('mellon_api')
app = create_flask_app()

def register_flask_app():
    interface.alsoProvides(app, mellon_api.IFlaskApplication)
    sm = component.getSiteManager()
    sm.registerUtility(app, mellon_api.IFlaskApplication) #give components access to app config

def configure_flask_app():
    m = get_registered_app()
    config_settings = m['vgetter'].get('Flask', default={})
    
    for k in config_settings:
        if k not in app.config:
            app.config[k] = config_settings[k]

def main():
    args = application.getScriptArgumentParser(DESCRIPTION).parse_args()
    # we'll override the core ZCML initializer with our own. then create the
    # base mellon application and init the component registry with the 
    # yaml-based zcml entry points
    mellon.mellon.Mellon.app_zcml = (mellon_api, 'configure.zcml')
    create_and_register_app(args.config_file, args.verbose, args.debug)
    component.getUtility(IMellonApplication).configure()
    #create, register, and run the application
    register_flask_app()
    configure_flask_app()
    component.getUtility(mellon_api.IFlaskApplication).run()

if __name__ == '__main__':
    main()