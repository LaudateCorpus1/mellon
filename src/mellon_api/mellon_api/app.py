import os
from zope import component
from zope import interface
import flask
from flask_restless import APIManager
from sparc.configuration.container import application
import mellon
import mellon_api
from mellon import IMellonApplication
from mellon.mellon import create_and_register_app, get_registered_app
from mellon_plugin.reporter.sqlalchemy.orm import models as mellon_models
from mellon_plugin.reporter.sqlalchemy.orm.workflow import models as workflow_models
from .sa import ISASession

from sparc.logging import logging
logger = logging.getLogger(__name__)

DESCRIPTION="""\
Mellon Restful API server.
"""

def register_flask_app():
    m = get_registered_app()
    sm = component.getSiteManager()
    
    kwargs = m['vgetter'].get('Flask', 'kwargs', default={})
    app = flask.Flask('mellon_api', **kwargs)
    interface.alsoProvides(app, mellon_api.IFlaskApplication)
    sm.registerUtility(app, mellon_api.IFlaskApplication) #hookable event
    logger.debug('new mellon_api.IFlaskApplication singleton registered')
    
    api = APIManager(app, 
                     session=component.getUtility(ISASession),
                     preprocessors=component.getUtility(mellon_api.IFlaskRestApiPreprocessors, name='mellon_api.preprocessors_global'),
                     postprocessors=component.getUtility(mellon_api.IFlaskRestApiPostprocessors, name='mellon_api.postprocessors_global'))
    add_api_resources(api)
    interface.alsoProvides(api, mellon_api.IFlaskRestApiApplication)
    sm.registerUtility(api, mellon_api.IFlaskRestApiApplication) #hookable event
    logger.debug('new mellon_api.IFlaskRestApiApplication singleton registered')

def configure_flask_app():
    m = get_registered_app()
    config_settings = m['vgetter'].get('Flask', 'settings', default={})
    if 'SECRET_KEY' not in config_settings:
        config_settings['SECRET_KEY'] = os.urandom(24) # sign cookies (and other stuff)
    else:
        config_settings['SECRET_KEY'] = bytes(config_settings['SECRET_KEY'], encoding='latin-1')
    
    app = component.getUtility(mellon_api.IFlaskApplication)
    for k in config_settings:
        app.config[k] = config_settings[k]
    logger.debug('mellon_api.IFlaskApplication singleton configured with runtime settings from Mellon yaml config.')

def get_api_endpoint_kwargs(endpoint):
    m = get_registered_app()
    kwargs = m['vgetter'].get('FlaskRestless', 'settings', 'default', default={})
    kwargs.update(m['vgetter'].get('FlaskRestless', 'settings', endpoint.lower(), default={}))
    kwargs['preprocessors'] = component.queryUtility(mellon_api.IFlaskRestApiPreprocessors, name='mellon_api.preprocessors_'+endpoint.lower())
    kwargs['postprocessors'] = component.queryUtility(mellon_api.IFlaskRestApiPostprocessors, name='mellon_api.postprocessors_'+endpoint.lower())
    return kwargs
    

def add_api_resources(api):
    api.create_api(mellon_models.Secret, 
                   methods=['GET','PATCH'],
                   **get_api_endpoint_kwargs('Secret'))

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