import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin

from zope import component
from mellon_plugin.reporter.sqlalchemy.orm.query import interfaces as qry_iface
from mellon_plugin.reporter.sqlalchemy.orm.workflow.testing import MELLON_SA_ORM_WORKFLOW_RUNTIME_LAYER
from mellon_plugin.reporter.sqlalchemy.orm import models as mellon_models
from mellon_plugin.reporter.sqlalchemy.orm.workflow import models as workflow_models
from mellon_plugin.reporter.sqlalchemy.orm.workflow import interfaces as workflow

MELLON_SA_ORM_WORKFLOW_RUNTIME_LAYER.verbose = True
class MellonOrmQueryTestCase(unittest.TestCase):
    layer = MELLON_SA_ORM_WORKFLOW_RUNTIME_LAYER
    
    def setUp(self):
        self.layer.create_complex_model()
        self.layer.session.flush()
        self.rrm = component.getUtility(qry_iface.ISAResultRowModel)
    
    def tearDown(self):
        self.layer.session.rollback()
    
    def test_workflow_core_related_model_registration(self):
        rmodels = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.workflow.core_related_models")
        self.assertIn(workflow_models.SecretSeverity, rmodels.models())
    
        
    def test_workflow_basic_query_results_secret(self):
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.workflow.core_related_models")
        #simplest search will be for a secret, it should only return based on the
        #total count of secrets in db (other would return many-to-one results)
        q = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    mellon_models.Secret,
                    core_models.models()
                    )
        self.assertEqual(q.count(), 3)
        status = self.rrm.first(workflow.ISASecretStatus, q.order_by(mellon_models.Secret.id).first())
        self.assertEqual(status.secret_id, 'secret_1')
        self.assertEqual(status.token, 'default_status')

class test_suite(test_suite_mixin):
    layer = MELLON_SA_ORM_WORKFLOW_RUNTIME_LAYER
    package = 'mellon_plugin.reporter.sqlalchemy.orm.workflow.query'
    module = 'query'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonOrmQueryTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])