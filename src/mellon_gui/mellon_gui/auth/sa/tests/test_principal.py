import os.path
import unittest
import zope.testrunner

from zope import component
from mellon_gui.sa import ISASession
from mellon_gui.auth.testing import MELLON_WEB_APP_AUTH_RUNTIME_LAYER

from sparc.login.identification.exceptions import InvalidIdentification
from sparc.login.principal import IPrincipalManager, IPrincipal

class MellonWebAppPrincipalTestCase(unittest.TestCase):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def setUp(self):
        self.session = component.getUtility(ISASession)
        self.mgr = component.getUtility(IPrincipalManager)
    
    def tearDown(self):
        self.session.rollback()
    
    def test_mgr_generate(self):
        prcpl1 = self.mgr.generate()
        self.assertTrue(IPrincipal.providedBy(prcpl1))
        try: # PY 2 3
            basestring
        except NameError:
            basestring = str
        self.assertTrue(isinstance(prcpl1.getId(), basestring))
        
        prcpl2 = self.mgr.generate()
        self.assertEqual(prcpl1, prcpl1)
        self.assertNotEqual(prcpl1, prcpl2)
    
    def test_mgr_create(self):
        with self.assertRaises(InvalidIdentification):
            self.mgr.create('wont_work')
    
    def test_mgr_get(self):
        prcpl1 = self.mgr.generate()
        copy = self.mgr.get(prcpl1)
        self.assertEqual(prcpl1, copy)
        
        with self.assertRaises(InvalidIdentification):
            self.mgr.get('invalid')
    
    def test_mgr_contains(self):
        prcpl1 = self.mgr.generate()
        self.assertTrue(self.mgr.contains(prcpl1))
        self.assertFalse(self.mgr.contains('invalid'))
    
    def test_mgr_remove(self):
        prcpl1 = self.mgr.generate()
        self.mgr.remove(prcpl1.getId())
        with self.assertRaises(InvalidIdentification):
            self.mgr.get(prcpl1.getId())
        with self.assertRaises(InvalidIdentification):
            self.mgr.remove('invalid')
    
    def test_mgr_discard(self):
        prcpl1 = self.mgr.generate()
        self.mgr.discard(prcpl1.getId())
        with self.assertRaises(InvalidIdentification):
            self.mgr.get(prcpl1.getId())
        self.mgr.discard('invalid') #silent
        
    
class test_suite(object):
    layer = MELLON_WEB_APP_AUTH_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonWebAppPrincipalTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
