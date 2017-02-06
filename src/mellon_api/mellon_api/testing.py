from multiprocessing import Process
from mellon_plugin.reporter.sqlalchemy.orm.testing import MellonOrmRuntimeReporterLayer
import mellon
import mellon_api
from mellon_api.app import create_eve_app

class MellonApiRuntimeLayer(MellonOrmRuntimeReporterLayer):
    
    def setUp(self, config=None):
        mellon.mellon.Mellon.app_zcml = (mellon_api, 'configure.zcml')
        super(MellonApiRuntimeLayer, self).setUp()
        self.eve_app = create_eve_app()
    
    def tearDown(self):
        self.stopApi()
        super(MellonApiRuntimeLayer, self).tearDown()
    
    eve_process = None
    
    def startApi(self):
        if not self.eve_process:
            self.eve_process = Process(target=self.eve_app.run())
            self.eve_process.start()
    
    def stopApi(self):
        if self.eve_process:
            self.eve_process.terminate()
            self.eve_process.join()

MELLON_API_RUNTIME_LAYER = MellonApiRuntimeLayer(mellon_api)


class MellonApiExecutedLayer(MellonApiRuntimeLayer):
    
    def setUp(self):
        super(MellonApiExecutedLayer, self).setUp()
        self.create_full_model(count=200)
        self.session.commit()
        self.startApi()

MELLON_API_EXECUTED_LAYER = MellonApiExecutedLayer(mellon_api)