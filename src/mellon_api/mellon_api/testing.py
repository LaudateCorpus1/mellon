from zope import component
import json
#from multiprocessing import Process
from mellon_plugin.reporter.sqlalchemy.orm.testing import MellonOrmRuntimeReporterLayer
import mellon
import mellon_api
import mellon_api.sa
from mellon_api.app import register_flask_app, configure_flask_app
from base64 import b64encode

from sparc.logging import logging
logger = logging.getLogger(__name__)

class MellonApiRuntimeLayer(MellonOrmRuntimeReporterLayer):
    """
    Keep in mind the 2 different contexts for DB interaction.  From the parent
    class, self.session will be available via the reporter orm package.
    In addition, the flask registration will create an independent 
    engine/session.
    """
    
    def setUp(self, config=None):
        mellon.mellon.Mellon.app_zcml = (mellon_api, 'configure.zcml')
        super(MellonApiRuntimeLayer, self).setUp(config=config)
        
        register_flask_app()
        configure_flask_app()
        self.flask_app = component.getUtility(mellon_api.IFlaskApplication)
        self.rest_api = component.getUtility(mellon_api.IFlaskRestApiApplication)
        if not self.debug:
            self.flask_app.logger.disabled = True
        self.flask_app.config['TESTING'] = True
        #see http://flask.pocoo.org/docs/0.12/testing/
        self.client = self.flask_app.test_client()
        
        #flask-restless issues sessions commits...this is bad for testing rollback
        session=component.getUtility(mellon_api.sa.ISASession)
        self._session_commit = session.commit
        session.commit = session.flush
    
    def tearDown(self):
        session = component.queryUtility(mellon_api.sa.ISASession)
        if session:
            session.commit = self._session_commit # reset this to normal
            session.rollback()
            session.remove()
        super(MellonApiRuntimeLayer, self).tearDown()

    def get_json(self, url_endpoint_request, basicauth=None):
        r = self.get_response(url_endpoint_request, basicauth)
        return json.loads(r.get_data(as_text=True))
    
    def get_response(self, url_endpoint_request, basicauth=None):
        headers = {}
        if basicauth:
            username, password = basicauth[0], basicauth[1]
            bts = bytes("{0}:{1}".format(username, password),encoding='latin-1')
            headers['Authorization'] = 'Basic ' + b64encode(bts).decode('latin-1')
        return self.client.get(url_endpoint_request, headers=headers)
    
    
MELLON_API_RUNTIME_LAYER = MellonApiRuntimeLayer(mellon_api)
