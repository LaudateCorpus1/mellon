from zope import component
from zope import interface
from flask import Flask, Blueprint
from flask_restplus import Api
from sparc.configuration.container import application
import mellon
import mellon_api
from mellon import IMellonApplication
from mellon.mellon import create_and_register_app, get_registered_app

from sparc.logging import logging
logger = logging.getLogger(__name__)

DESCRIPTION="""\
Mellon Restful API server.
"""

def register_flask_app():
    sm = component.getSiteManager()
    
    blueprint = Blueprint('mellon_api', __name__, url_prefix='/api')
    api = Api(version='1.0', title='Mellon API',
          description='Mellon ORM workflow API.')
    api.init_app(blueprint)
    interface.alsoProvides(api, mellon_api.IFlaskRestApiApplication)
    sm.registerUtility(api, mellon_api.IFlaskRestApiApplication) #hookable event
    logger.debug('new mellon_api.IFlaskRestApiApplication singleton registered')

    app = Flask('mellon_api')
    app.register_blueprint(blueprint)
    interface.alsoProvides(app, mellon_api.IFlaskApplication)
    sm.registerUtility(app, mellon_api.IFlaskApplication) #hookable event
    logger.debug('new mellon_api.IFlaskApplication singleton registered')

def configure_flask_app():
    m = get_registered_app()
    config_settings = m['vgetter'].get('Flask', 'settings', default={})
    
    app = component.getUtility(mellon_api.IFlaskApplication)
    for k in config_settings:
        if k not in app.config:
            app.config[k] = config_settings[k]
    logger.debug('mellon_api.IFlaskApplication singleton configured with runtime settings from Mellon yaml config.')

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
    #if args.debug:
    #    app.logger.addHandler(handler)
    #    #app.config['DEBUG'] = True
    #    app.logger.setLevel(logging.DEBUG)
    component.getUtility(mellon_api.IFlaskApplication).run()

if __name__ == '__main__':
    main()