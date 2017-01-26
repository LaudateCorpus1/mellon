import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin

from ..testing import MELLON_SA_ORM_REPORTER_EXECUTED_LAYER
from .. import models


class MellonOrmReporterTestCase(unittest.TestCase):
    layer = MELLON_SA_ORM_REPORTER_EXECUTED_LAYER
    
    def setUp(self):
        super(MellonOrmReporterTestCase, self).setUp()
    
    def test_reporter(self):
        # now check orm
        self.assertEquals(len(self.layer.session.query(models.Secret).all()), 2)

class test_suite(test_suite_mixin):
    layer = MELLON_SA_ORM_REPORTER_EXECUTED_LAYER
    package = 'mellon_plugin.reporter.sqlalchemy.orm'
    module = 'db'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonOrmReporterTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])