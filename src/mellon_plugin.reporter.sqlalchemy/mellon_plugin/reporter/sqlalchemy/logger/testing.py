from zope import component
from mellon.testing import MellonApplicationRuntimeLayer
from mellon.reporters.memory.memory import reset_report
import mellon_plugin.reporter.sqlalchemy.logger

from .interfaces import IDBReporter

class MellonLoggerRuntimeReporterLayer(MellonApplicationRuntimeLayer):
    def setUp(self):
        self.config = \
            {
             'SQLAlchemyLoggerReporter':
                {'SQLAlchemyReporter':
                    {'SQLAlchemyEngine':
                        {'dsn': 'sqlite:///:memory:'},
                     }
                 },
             'MellonFileProviderFactory':
                {'name': 'mellon.factories.test.file_provider_for_testing'},
             'ZopeComponentConfiguration':
                {
                 'zcml': [ {'package': 'mellon_plugin.reporter.sqlalchemy.logger', 'file': 'ftesting.zcml'}]
                }
            }
        super(MellonLoggerRuntimeReporterLayer, self).setUp()
        self.reporter = component.getUtility(IDBReporter)
    
    def tearDown(self):
        reset_report()
        super(MellonLoggerRuntimeReporterLayer, self).tearDown()
MELLON_SA_LOGGER_REPORTER_RUNTIME_LAYER = MellonLoggerRuntimeReporterLayer(mellon_plugin.reporter.sqlalchemy)

class MellonLoggerExecutedReporterLayer(MellonLoggerRuntimeReporterLayer):
    def setUp(self):
        super(MellonLoggerExecutedReporterLayer, self).setUp()
        self.app.go()
MELLON_SA_LOGGER_REPORTER_EXECUTED_LAYER = MellonLoggerExecutedReporterLayer(mellon_plugin.reporter.sqlalchemy.logger)