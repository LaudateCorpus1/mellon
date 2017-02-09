from zope import component
#from multiprocessing import Process
from mellon_plugin.reporter.sqlalchemy.orm.testing import MellonOrmRuntimeReporterLayer
import mellon
import mellon_api
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
        super(MellonApiRuntimeLayer, self).setUp()
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
    
    def tearDown(self):
        #self.stopApi() #calls commit to Flask db session via event subscription (also removes scoped Flask session)
        super(MellonApiRuntimeLayer, self).tearDown()
    """
    app_process = None
    app_server_name = 'localhost:5000'
    app_url = 'http://' + app_server_name
    
    def startApi(self):
        if not self.app_process:
            app = component.getUtility(mellon_api.IFlaskApplication)
            app.config['TESTING'] = True
            #app.config['DEBUG'] = self.debug
            app.config['SERVER_NAME'] =  self.app_server_name
            self.app_process = Process(target=app.run)
            self.app_process.start()
    
    def stopApi(self):
        if self.app_process:
            self.app_process.terminate()
            self.app_process.join()
    """

MELLON_API_RUNTIME_LAYER = MellonApiRuntimeLayer(mellon_api)


class MellonApiExecutedLayer(MellonApiRuntimeLayer):
    
    def setUp(self):
        super(MellonApiExecutedLayer, self).setUp()
        self.create_full_model(count=75)
        self.session.flush()
        #self.startApi()
    
    def tearDown(self):
        self.session.rollback()
        super(MellonApiExecutedLayer, self).tearDown()

MELLON_API_EXECUTED_LAYER = MellonApiExecutedLayer(mellon_api)