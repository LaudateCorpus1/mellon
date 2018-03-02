import os.path
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin

from mellon_gui.sa import ISAEngine, ISASession
from mellon_gui.testing import MELLON_WEB_APP_RUNTIME_LAYER

class MellonGuiSaTestCase(unittest.TestCase):
    layer = MELLON_WEB_APP_RUNTIME_LAYER
    
    def test_util_registrations(self):
        engine = component.getUtility(ISAEngine)
        self.assertTrue(ISAEngine.providedBy(engine))
        session = component.getUtility(ISASession)
        self.assertTrue(ISASession.providedBy(session))
    
    
class test_suite(test_suite_mixin):
    layer = MELLON_WEB_APP_RUNTIME_LAYER
    package = 'mellon_gui.sa.subscribers'
    module = 'bind_sa_to_app'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonGuiSaTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])