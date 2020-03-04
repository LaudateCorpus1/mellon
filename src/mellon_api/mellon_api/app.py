import os
from zope import component
from zope import interface
import flask
#import flask_restful
from jsonapi.base.errors import Error, error_to_response
import jsonapi.flask
from jsonapi.flask.api import to_response
import jsonapi.sqlalchemy
from .sa import ISASession
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

class MellonAPI(jsonapi.flask.FlaskAPI):
    
    def handle_request(self, *args, **kwargs):
        #import pdb;pdb.set_trace
        try:
            for preprocessor in component.getUtility(mellon_api.IFlaskRestApiPreprocessors):
                preprocessor()
        except Error as e:
            #import pdb;pdb.set_trace()
            return to_response(error_to_response(e, self.dump_json))
        return super(MellonAPI, self).handle_request(*args, **kwargs)

def register_flask_app():
    m = get_registered_app()
    sm = component.getSiteManager()
    
    kwargs = m['vgetter'].get_value('Flask', 'kwargs', default={})
    app = flask.Flask('mellon_api', **kwargs)
    interface.alsoProvides(app, mellon_api.IFlaskApplication)
    sm.registerUtility(app, mellon_api.IFlaskApplication) #hookable event
    logger.debug('new mellon_api.IFlaskApplication singleton registered')
    
    #We init the api without reference to the app because then api.resources
    #will be populated with the all route Resources (which is needed by the 
    #internals of mellon_api). 
    db = jsonapi.sqlalchemy.Database(sessionmaker=component.getUtility(ISASession))
    api = MellonAPI("/api", db)
    #api = flask_restful.Api()
    interface.alsoProvides(api, mellon_api.IFlaskRestApiApplication)
    sm.registerUtility(api, mellon_api.IFlaskRestApiApplication) #hookable event (resources)
    #at this point api.resources is populated.  No new routes after this!!!
    api.init_app(app)
    #api.app = app
    logger.debug('new mellon_api.IFlaskRestApiApplication singleton registered')

def configure_flask_app():
    m = get_registered_app()
    config_settings = m['vgetter'].get_value('Flask', 'settings', default={})
    if 'SECRET_KEY' not in config_settings:
        config_settings['SECRET_KEY'] = os.urandom(24) # sign cookies (and other stuff)
    else:
        config_settings['SECRET_KEY'] = bytes(config_settings['SECRET_KEY'], encoding='latin-1')
    
    app = component.getUtility(mellon_api.IFlaskApplication)
    for k in config_settings:
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
    component.getUtility(mellon_api.IFlaskApplication).run()

if __name__ == '__main__':
    main()