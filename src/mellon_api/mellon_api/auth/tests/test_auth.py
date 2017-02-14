import os.path
import unittest
import zope.testrunner

from zope import component
import mellon_api
from ..auth import auth_func
from ..testing import MELLON_API_AUTH_RUNTIME_LAYER

class MellonApiAuthTestCase(unittest.TestCase):
    layer = MELLON_API_AUTH_RUNTIME_LAYER
    model_count = 1
    
    def setUp(self):
        self.endpoint = "/api/secrets"
        self.layer.create_full_model(count=self.model_count)
        self.layer.session.flush()
    
    def tearDown(self):
        self.layer.session.rollback()
    
    def test_preprocessor_injection(self):
        pp = component.getUtility(mellon_api.IFlaskRestApiPreprocessors, name='mellon_api.preprocessors_global')
        self.assertEquals(pp['GET_SINGLE'][0], auth_func)
    
    
class test_suite(object):
    layer = MELLON_API_AUTH_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonApiAuthTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
