import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from sqlalchemy.engine import reflection
from .. import models
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
        self.assertTrue(models.SecretStatus.__tablename__ in insp.get_table_names())
        
    def test_model_SecretStatus(self):
        status = models.SecretStatus(token='token_1', secret_id=self.models['Secret'].id)
        self.layer.session.add(status)
        self.layer.session.flush()
        
        status = self.layer.session.query(models.SecretStatus).\
                            filter(
                                models.SecretStatus.secret_id == self.models['Secret'].id).\
                                first()
        self.assertEquals(status.token, 'token_1')
        
    def test_model_SecretSeverity(self):
        status = models.SecretSeverity(token='token_A', secret_id=self.models['Secret'].id)
        self.layer.session.add(status)
        self.layer.session.flush()
        
        status = self.layer.session.query(models.SecretSeverity).\
                            filter(
                                models.SecretSeverity.secret_id == self.models['Secret'].id).\
                                first()
        self.assertEquals(status.token, 'token_A')
    

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