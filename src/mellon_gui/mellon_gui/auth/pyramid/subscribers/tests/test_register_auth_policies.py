import os.path
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin

from pyramid.interfaces import IAuthenticationPolicy
from mellon_gui.auth.testing import MELLON_WEB_APP_AUTH_RUNTIME_LAYER

class MellonPolicyRegistrationTestCase(unittest.TestCase):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def test_authn_policy_registration(self):
        policy = component.getUtility(IAuthenticationPolicy)
        self.assertTrue(IAuthenticationPolicy.providedBy(policy))
    
    
class test_suite(test_suite_mixin):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    package = 'mellon_gui.auth.pyramid.subscribers'
    module = 'register_auth_policies'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonPolicyRegistrationTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])