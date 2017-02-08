import os.path
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin

from mellon_api.sa import ISAEngine, ISASession
from mellon_api.sa.testing import MELLON_API_SA_RUNTIME_LAYER
import mellon_api.sa.subscribers.bind_sa_to_app

class MellonApiwargsTestCase(unittest.TestCase):
    layer = MELLON_API_SA_RUNTIME_LAYER
    
    def test_util_registrations(self):
        engine = component.getUtility(ISAEngine)
        self.assertTrue(ISAEngine.providedBy(engine))
        session = component.getUtility(ISASession)
        self.assertTrue(ISASession.providedBy(session))
        self.assertTrue(mellon_api.sa.subscribers.bind_sa_to_app._test_commit_request_registrations)
    
class test_suite(test_suite_mixin):
    layer = MELLON_API_SA_RUNTIME_LAYER
    package = 'mellon_api.sa.subscribers'
    module = 'bind_sa_to_app'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonApiwargsTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])