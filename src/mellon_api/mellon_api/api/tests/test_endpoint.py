import os.path
import unittest
import zope.testrunner

from mellon_api import testing
from zope import component
from .. import IAPISAEndpoint, IAPISAEndpointLookup

#testing.MELLON_API_RUNTIME_LAYER.debug=True
class MellonApiAuthorizationContextTestCase(unittest.TestCase):
    layer = testing.MELLON_API_RUNTIME_LAYER
    model_count = 75
    
    def setUp(self):
        self.endpoint = '/authorization-contexts'
        self.layer.create_full_model(count=self.model_count)
        self.layer.session.flush()
    
    def tearDown(self):
        self.layer.session.rollback()
    
    def test_endpoint_lookup(self):
        looker = component.getUtility(IAPISAEndpointLookup)
        self.assertTrue(IAPISAEndpoint.providedBy(looker.lookup('authorization-context')))
    
    def test_get_single(self):
        json = self.layer.get_json(self.endpoint+'/authorization_context_1')
        self.assertEqual(json['data']['type'], 'authorization_context')
        self.assertEqual(json['data']['attributes']['name'], 'authorization context 1')
    
    def test_get_page_default(self):
        json = self.layer.get_json(self.endpoint)
        self.assertEqual(len(json['data']), self.layer.config['ResourcePagination']['max_limit'])
    
    def test_get_page_2(self):
        json = self.layer.get_json(self.endpoint+'?arg1=value1&arg2=value2&arg1=value3')
        json = self.layer.get_json(json['links']['next'])
        self.assertEqual(len(json['data']), self.model_count - self.layer.config['ResourcePagination']['max_limit'])
    

class test_suite(object):
    layer = testing.MELLON_API_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonApiAuthorizationContextTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
