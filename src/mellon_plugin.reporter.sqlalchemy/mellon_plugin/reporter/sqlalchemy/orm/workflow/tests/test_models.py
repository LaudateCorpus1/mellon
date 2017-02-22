import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from sqlalchemy.engine import reflection
from mellon_plugin.reporter.sqlalchemy.orm.workflow import models
from ..testing import MELLON_SA_ORM_WORKFLOW_RUNTIME_LAYER

class MellonORMReporterTestCase(unittest.TestCase):
    layer = MELLON_SA_ORM_WORKFLOW_RUNTIME_LAYER
    
    def setUp(self):
        #create a full stack secret
        self.models = self.layer.create_full_model()

    def tearDown(self):
        self.layer.session.rollback()
    
    def test_schema(self):
        insp = reflection.Inspector.from_engine(self.layer.engine)
        columns = insp.get_columns(models.Secret.__tablename__)
        # 'status_token' in table's columns
        self.assertTrue(models.Secret.status_token.key in map(lambda c: c['name'], columns))
        # 'severity_token' in table's columns
        self.assertTrue(models.Secret.severity_token.key in map(lambda c: c['name'], columns))
    

class test_suite(test_suite_mixin):
    layer = MELLON_SA_ORM_WORKFLOW_RUNTIME_LAYER
    package = 'mellon_plugin.reporter.sqlalchemy.orm.workflow'
    module = 'models'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonORMReporterTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])