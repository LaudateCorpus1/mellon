import os.path
import unittest
import zope.testrunner

from zope import component
from mellon_api.sa import ISASession
from ..testing import MELLON_API_AUTH_RUNTIME_LAYER

from .. import IUserPasswordAuthenticationManager, exc

class MellonApiPasswordTestCase(unittest.TestCase):
    layer = MELLON_API_AUTH_RUNTIME_LAYER
    
    def setUp(self):
        self.session = component.getUtility(ISASession)
        self.manager = IUserPasswordAuthenticationManager(self.session)
    
    def tearDown(self):
        self.session.rollback()
    
    def test_session_password_adapter_create(self):
        user1 = self.manager.create('user1', 'password1')
        self.assertEqual(user1.principal_id, 1)
        
        with self.assertRaises(ValueError):
            self.manager.create('user1', 'password1')
            
        user2 = self.manager.create('user2', 'password2')
        self.assertEqual(user2.principal_id, 2)
        
        user1_a = self.manager.create('user1_a', 'password1', principal_id=1)
        self.assertEqual(user1.principal_id, user1_a.principal_id)
        
        with self.assertRaises(KeyError):
            self.manager.create('invalid_principal_id_spec', 'password1', principal_id=10)
        
    
    def test_session_password_adapter_check_authentication(self):
        with self.assertRaises(KeyError):
            self.manager.check_authentication('invalid_user', 'password')
        
        user1 = self.manager.create('user1', 'password1')
        self.assertIsNone(self.manager.check_authentication(user1.username, 'password1'))
        
        with self.assertRaises(exc.MellonAPIInvalidPassword):
            self.manager.check_authentication(user1.username, 'invalid_password')
    
    def test_session_password_adapter_update_password(self):
        user1 = self.manager.create('user1', 'password1')
        self.manager.update_password('user1', 'password2')
        self.assertIsNone(self.manager.check_authentication(user1.username, 'password2'))
        
        #empty strings still create valid passwords
        self.manager.update_password('user1', '')
        self.assertIsNone(self.manager.check_authentication(user1.username, ''))
        self.assertGreater(len(user1.password_crypt), 0)
        
    def test_session_password_adapter_update_username(self):
        user1 = self.manager.create('user1', 'password1')
        self.manager.create('user2', 'password2')
        
        with self.assertRaises(ValueError):
            self.manager.update_username(user1.username, 'user2')
        self.assertIsNone(self.manager.update_username(user1.username, 'new_name'))
        self.assertEqual(user1.username, 'new_name')
        
    def test_session_password_adapter_disable(self):
        user1 = self.manager.create('user1', '')
        self.manager.disable(user1.username)
        with self.assertRaises(exc.MellonAPIUserIsDisabled):
            self.manager.check_authentication(user1.username, '')
        
    def test_session_password_adapter_delete(self):
        user1 = self.manager.create('user1', '')
        self.assertEqual(user1.principal_id, 1)
        self.assertIsNone(self.manager.check_authentication('user1', ''))
        self.manager.delete('user1')
        with self.assertRaises(KeyError):
            self.manager.check_authentication('user1', '')
        #new user with same username is a different principal
        user1a = self.manager.create('user1', '')
        self.assertEqual(user1a.principal_id, 2)

class test_suite(object):
    layer = MELLON_API_AUTH_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonApiPasswordTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
