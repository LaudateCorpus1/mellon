import os.path
import unittest
import zope.testrunner

from zope import component
from mellon_gui.sa import ISASession
from mellon_gui.auth.testing import MELLON_WEB_APP_AUTH_RUNTIME_LAYER

from sparc.login.identification.exceptions import InvalidIdentification
from sparc.login.credentials import ICredentialIdentityManager, ICredentialIdentity
from sparc.login.principal import IPrincipal
from .. import models

class MellonWebAppUsernameTestCase(unittest.TestCase):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def setUp(self):
        self.session = component.getUtility(ISASession)
        self.mgr = component.getUtility(ICredentialIdentityManager)
    
    def tearDown(self):
        self.session.rollback()
    
    def test_principal_adaptation_from_user(self):
        id1 = self.mgr.generate('user1')
        user = self.session.query(models.UserPasswordAuthentication).get(id1.getId())
        prcpl1 = IPrincipal(id1)
        self.assertEqual(user.username, id1.getId())
        self.assertEqual(str(user.principal_id), prcpl1.getId())
    
    def test_mgr_generate(self):
        user1 = self.mgr.generate('user1')
        self.assertTrue(ICredentialIdentity.providedBy(user1))
        try: # PY 2 3
            basestring
        except NameError:
            basestring = str
        self.assertTrue(isinstance(user1.getId(), basestring))
        
        user2 = self.mgr.generate() # no hint
        self.assertEqual(user1, user1)
        self.assertNotEqual(user1, user2)
        self.assertGreater(len(user2.getId()), 0)
        
        user3 = self.mgr.generate('user1') #conflict with user1...should auto-increment
        self.assertEqual(user3.getId(), 'user11')
    
    def test_mgr_create(self):
        user1 = self.mgr.create('user1')
        with self.assertRaises(InvalidIdentification):
            self.mgr.create('user1')
        self.assertTrue(ICredentialIdentity.providedBy(user1))
    
    def test_mgr_get(self):
        user1 = self.mgr.generate()
        copy = self.mgr.get(user1)
        self.assertEqual(user1, copy)
        
        with self.assertRaises(InvalidIdentification):
            self.mgr.get('invalid')
    
    def test_mgr_contains(self):
        user1 = self.mgr.generate()
        self.assertTrue(self.mgr.contains(user1))
        self.assertFalse(self.mgr.contains('invalid'))
    
    def test_mgr_remove(self):
        user1 = self.mgr.generate()
        self.mgr.remove(user1.getId())
        with self.assertRaises(InvalidIdentification):
            self.mgr.get(user1.getId())
        with self.assertRaises(InvalidIdentification):
            self.mgr.remove('invalid')
    
    def test_mgr_discard(self):
        user1 = self.mgr.generate()
        self.mgr.discard(user1.getId())
        with self.assertRaises(InvalidIdentification):
            self.mgr.get(user1.getId())
        self.mgr.discard('invalid') #silent
    
    def test_mgr_update(self):
        user1 = self.mgr.generate()
        orig_id = user1.getId()
        self.mgr.update(user1, 'new_name')
        
        with self.assertRaises(InvalidIdentification):
            self.mgr.get(orig_id)
        
        self.mgr.get('new_name') #no exception
        
    
class test_suite(object):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonWebAppUsernameTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
