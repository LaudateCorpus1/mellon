from zope import component
from multiprocessing import Process
from mellon_plugin.reporter.sqlalchemy.orm.testing import MellonOrmRuntimeReporterLayer
import mellon
import mellon_api
from mellon_api.app import create_flask_app, register_flask_app, configure_flask_app

class MellonApiRuntimeLayer(MellonOrmRuntimeReporterLayer):
    """
    Keep in mind the 2 different contexts for DB interaction.  From the parent
    class, self.session will be available via the reporter orm package.
    In addition, the flask registration will create an independent 
    engine/session.
    """
    
    def setUp(self, config=None):
        mellon.mellon.Mellon.app_zcml = (mellon_api, 'configure.zcml')
        super(MellonApiRuntimeLayer, self).setUp()
        register_flask_app()
        configure_flask_app()
    
    def tearDown(self):
        self.stopApi() #calls commit to Flask db session via event subscription (also removes scoped Flask session)
        super(MellonApiRuntimeLayer, self).tearDown()
        mellon_api.app.app = create_flask_app() #reset the global
    
    app_process = None
    
    def startApi(self):
        if not self.app_process:
            app = component.getUtility(mellon_api.IFlaskApplication)
            self.app_process = Process(target=app.run, kwargs={'debug':self.debug})
            self.app_process.start()
    
    def stopApi(self):
        if self.app_process:
            self.app_process.terminate()
            self.app_process.join()

MELLON_API_RUNTIME_LAYER = MellonApiRuntimeLayer(mellon_api)


class MellonApiExecutedLayer(MellonApiRuntimeLayer):
    
    def setUp(self):
        super(MellonApiExecutedLayer, self).setUp()
        self.create_full_model(count=200)
        self.session.flush()
        self.startApi()
    
    def tearDown(self):
        self.session.rollback()
        super(MellonApiExecutedLayer, self).tearDown()

MELLON_API_EXECUTED_LAYER = MellonApiExecutedLayer(mellon_api)