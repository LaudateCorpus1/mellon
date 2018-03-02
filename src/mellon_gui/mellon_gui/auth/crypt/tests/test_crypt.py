import os.path
import unittest
import zope.testrunner

from zope import component
from mellon_gui.auth.testing import MELLON_WEB_APP_AUTH_RUNTIME_LAYER

from sparc.login.credentials.authn.crypt import ICrypter
from ..crypt import user_password_crypt_context

class MellonWebAppCryptTestCase(unittest.TestCase):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def test_crypt_utility(self):
        crypter = component.getUtility(ICrypter)
        self.assertIs(crypter, user_password_crypt_context)
        hashed = crypter.hash('my secret'.encode('utf-8'))
        self.assertTrue(crypter.verify('my secret'.encode('utf-8'), hashed))
    

class test_suite(object):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonWebAppCryptTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
