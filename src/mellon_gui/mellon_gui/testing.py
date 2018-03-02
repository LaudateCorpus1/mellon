from mellon_plugin.reporter.sqlalchemy.orm.testing import MellonOrmRuntimeReporterLayer
import mellon_gui

class MellonWebAppRuntimeLayer(MellonOrmRuntimeReporterLayer):
    
    def setUp(self, config=None):
        _config = {}
        if config:
            _config.update(config)
        self.config = _config
        super(MellonWebAppRuntimeLayer, self).setUp(config=_config)
        
        
        from mellon_gui import main
        settings = {}
        settings['mellon.config'] = self.config
        settings['mellon.verbose'] = str(self.verbose)
        settings['mellon.debug'] = str(self.debug)
        if self.debug:
            settings['pyramid.debug_all'] = 'True'
        app = main({}, **settings)
        self.pyramid_app = app
        from webtest import TestApp
        self.testapp = TestApp(app)

MELLON_WEB_APP_RUNTIME_LAYER = MellonWebAppRuntimeLayer(mellon_gui)