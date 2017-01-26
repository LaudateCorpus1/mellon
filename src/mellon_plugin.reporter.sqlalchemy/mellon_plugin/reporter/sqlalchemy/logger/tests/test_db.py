import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from sqlalchemy import sql

from ..testing import MELLON_SA_LOGGER_REPORTER_EXECUTED_LAYER

class MellonSAReporterTestCase(unittest.TestCase):
    layer = MELLON_SA_LOGGER_REPORTER_EXECUTED_LAYER

    def get_rows(self):
        connection = self.layer.reporter.engine.connect()
        _return = []
        result = connection.execute(sql.select([self.layer.reporter.tables['secrets']]))
        for row in result:
            _return.append(row)
        result.close()
        connection.close()
        return _return

    def test_reporter(self):
        #self.assertFalse(self.layer.reporter.initialized())
        #self.layer.reporter.update_schema()
        self.assertTrue(self.layer.reporter.initialized())
        self.assertEquals(len(self.get_rows()), 2)
        

class test_suite(test_suite_mixin):
    layer = MELLON_SA_LOGGER_REPORTER_EXECUTED_LAYER
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