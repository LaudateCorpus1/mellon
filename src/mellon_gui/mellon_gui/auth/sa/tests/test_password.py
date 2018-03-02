import os.path
import unittest
import zope.testrunner

from zope import component
from mellon_gui.sa import ISASession
from mellon_gui.auth.testing import MELLON_WEB_APP_AUTH_RUNTIME_LAYER

from sparc.login.credentials.authn import IPasswordHashToken
from sparc.login.credentials.authn.crypt import ICrypter
from .. import models

class MellonWebAppPasswordTestCase(unittest.TestCase):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def setUp(self):
        self.session = component.getUtility(ISASession)
    
    def tearDown(self):
        self.session.rollback()
    
    def _create_user(self, token):
        prncpl = models.Principal()
        self.session.add(prncpl)
        self.session.flush() #generates the principal id
        user = models.UserPasswordAuthentication(username=token, 
                   principal_id=prncpl.id)
        self.session.add(user)
        return user
    
    def test_password_adaptation(self):
        #create an invalid credential identity
        id1 = component.createObject(u'sparc.login.credential_identity', '1')
        with self.assertRaises(TypeError): #unable to adapt
            IPasswordHashToken(id1)
        
        #create an associated db user
        self._create_user(id1.getId())
        hash_ = IPasswordHashToken(id1) #adaptation now works
        self.assertEqual(bool(hash_.token), False)
        
        hash_.token = 'some secret'
        hash_ = IPasswordHashToken(id1) #do the look-up again
        self.assertNotEqual(bool(hash_.token), False)
        self.assertNotEqual(bool(hash_.token), 'some secret')
        
        crypter = component.getUtility(ICrypter)
        self.assertTrue(crypter.verify('some secret', hash_.token))

class test_suite(object):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonWebAppPasswordTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
