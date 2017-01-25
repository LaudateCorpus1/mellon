import os.path
import unittest
from zope import component
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from mellon.testing import MellonRuntimeLayerMixin
from mellon.reporters.memory import memory
from mellon.sniffers.regex.tests.test_regex import MellonSnifferRegExTestCase
from mellon_plugin.reporter.sqlalchemy.logger import IDBReporter
from sqlalchemy import sql

base_path = os.path.dirname(__file__)

import mellon_plugin.reporter.sqlalchemy.logger
class MellonSAReporterLayer(MellonRuntimeLayerMixin):
    pass
MELLON_SA_LOGGER_REPORTER_RUNTIME_LAYER = MellonSAReporterLayer(mellon_plugin.reporter.sqlalchemy.logger)

class MellonSAReporterTestCase(unittest.TestCase):
    layer = MELLON_SA_LOGGER_REPORTER_RUNTIME_LAYER
    sm = component.getSiteManager()
    report = memory.report
    
    def __init__(self, *args, **kwargs):
        super(MellonSAReporterTestCase, self).__init__(*args, **kwargs)
        config = MellonSnifferRegExTestCase.config.copy()
        config.update(
                {
                 'SQLAlchemyReporter':
                    {'SQLAlchemyEngine':
                        {'dsn': 'sqlite:///:memory:'},
                     }
                }
            )
        self.layer.config.update(config)
        self.layer.config['ZCMLConfiguration'].extend(
                        [
                             {'package':'mellon.sniffers.regex'},
                             {'package':'mellon.factories.filesystem'},
                             {'package':'mellon_plugin.reporter.sqlalchemy.logger'}
                        ])
        self.layer.verbose = False
        self.layer.debug = False
        
        self.app = self.layer.create_registered_app()
        self.app.configure()
        self.reporter = component.getUtility(IDBReporter)
    
    def tearDown(self):
        memory.reset_report()
    
    def get_rows(self):
        connection = self.reporter.engine.connect()
        _return = []
        result = connection.execute(sql.select([self.reporter.tables['secrets']]))
        for row in result:
            _return.append(row)
        result.close()
        connection.close()
        return _return

    def test_reporter(self):
        self.assertFalse(self.reporter.initialized())
        self.reporter.update_schema()
        self.assertTrue(self.reporter.initialized())
        
        self.assertEquals(self.get_rows(), [])
        self.app.go()
        self.assertEquals(len(self.get_rows()), 4)
        

class test_suite(test_suite_mixin):
    layer = MELLON_SA_LOGGER_REPORTER_RUNTIME_LAYER
    package = 'mellon_plugin.reporter.sqlalchemy.logger'
    module = 'db'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonSAReporterTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])