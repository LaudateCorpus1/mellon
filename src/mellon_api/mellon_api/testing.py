from zope import component
import json
#from multiprocessing import Process
from mellon_plugin.reporter.sqlalchemy.orm.testing import MellonOrmRuntimeReporterLayer
import mellon
import mellon_api
import mellon_api.sa
from mellon_api.app import register_flask_app, configure_flask_app

from sparc.logging import logging
logger = logging.getLogger(__name__)

class MellonApiRuntimeLayer(MellonOrmRuntimeReporterLayer):
    """
    Keep in mind the 2 different contexts for DB interaction.  From the parent
    class, self.session will be available via the reporter orm package.
    In addition, the flask registration will create an independent 
    engine/session.
    """
    
    # Kinda dumb, but we need to store these objects as class-level to insure
    # ZCML tear-down doesn't destroy them.  Otherwise, we'd have to find cute
    # ways to reload the api routes...this is easier to deal with
    flask_app = None #Flask()
    rest_api = None #Api()
    
    def setUp(self, config=None):
        mellon.mellon.Mellon.app_zcml = (mellon_api, 'configure.zcml')
        super(MellonApiRuntimeLayer, self).setUp(config=config)
        if not MellonApiRuntimeLayer.flask_app:
            register_flask_app()
            configure_flask_app()
            MellonApiRuntimeLayer.flask_app = component.getUtility(mellon_api.IFlaskApplication)
            MellonApiRuntimeLayer.rest_api = component.getUtility(mellon_api.IFlaskRestApiApplication)
        else:
            sm = component.getSiteManager()
            sm.registerUtility(self.flask_app, mellon_api.IFlaskApplication)
            logger.debug('Registered existing mellon_api.IFlaskApplication singleton to new layer registry')
            sm.registerUtility(self.rest_api, mellon_api.IFlaskRestApiApplication)
            logger.debug('Registered existing mellon_api.IFlaskRestApiApplication singleton to new layer registry')
        MellonApiRuntimeLayer.flask_app.config['TESTING'] = True
        #see http://flask.pocoo.org/docs/0.12/testing/
        self.client = MellonApiRuntimeLayer.flask_app.test_client()
        
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
        #self.stopApi() #calls commit to Flask db session via event subscription (also removes scoped Flask session)
        super(MellonApiRuntimeLayer, self).tearDown()

    def get_json(self, url_endpoint_request):
        r = self.client.get(url_endpoint_request)
        #import pdb;pdb.set_trace()
        return json.loads(r.get_data(as_text=True))
MELLON_API_RUNTIME_LAYER = MellonApiRuntimeLayer(mellon_api)
