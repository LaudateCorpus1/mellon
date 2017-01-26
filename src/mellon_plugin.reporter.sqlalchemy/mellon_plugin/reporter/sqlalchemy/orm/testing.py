from mellon.testing import MellonApplicationRuntimeLayer
from mellon.reporters.memory.memory import reset_report
import mellon_plugin.reporter.sqlalchemy.orm
from .db import get_session

class MellonOrmRuntimeReporterLayer(MellonApplicationRuntimeLayer):
    def setUp(self):
        self.config = \
            {
             'SQLAlchemyORMReporter':
                {'SQLAlchemyReporter':
                    {'SQLAlchemyEngine':
                        {'dsn': 'sqlite:///:memory:'},
                     }
                 },
             'MellonFileProviderFactory':
                {'name': 'mellon.factories.test.file_provider_for_testing'},
             'ZCMLConfiguration':
                [
                    {'package':'mellon.sniffers.test'},
                    {'package':'mellon.factories.test'},
                    {'package':'mellon_plugin.reporter.sqlalchemy.orm'}
                 ]
            }
        super(MellonOrmRuntimeReporterLayer, self).setUp()
        self.session = get_session()
    
    def tearDown(self):
        reset_report()
        super(MellonOrmRuntimeReporterLayer, self).tearDown()
MELLON_SA_ORM_REPORTER_RUNTIME_LAYER = MellonOrmRuntimeReporterLayer(mellon_plugin.reporter.sqlalchemy)

class MellonOrmExecutedReporterLayer(MellonOrmRuntimeReporterLayer):
    def setUp(self):
        super(MellonOrmExecutedReporterLayer, self).setUp()
        self.app.go()
MELLON_SA_ORM_REPORTER_EXECUTED_LAYER = MellonOrmExecutedReporterLayer(mellon_plugin.reporter.sqlalchemy.orm)