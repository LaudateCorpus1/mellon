import os.path
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin

from mellon_gui.sa import ISAEngine
from mellon_gui.auth.sa import models
from mellon_gui.auth.testing import MELLON_WEB_APP_AUTH_RUNTIME_LAYER

class MellonAuthModelTestCase(unittest.TestCase):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def test_model_creation(self):
        engine = component.getUtility(ISAEngine)
        self.assertIn(models.Principal.__tablename__, engine.table_names())
        self.assertIn(models.UserPasswordAuthentication.__tablename__, engine.table_names())
    
    
class test_suite(test_suite_mixin):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    package = 'mellon_gui.auth.sa.subscribers'
    module = 'create_auth_models'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonAuthModelTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])