import os.path
import unittest
import zope.testrunner

import json
from mellon_api import testing

class MellonApiSecretsTestCase(unittest.TestCase):
    layer = testing.MELLON_API_RUNTIME_LAYER
    model_count = 75
    
    def setUp(self):
        self.endpoint = "/api/secrets"
        self.layer.create_full_model(count=self.model_count)
        self.layer.session.flush()
    
    def tearDown(self):
        self.layer.session.rollback()
    
    def test_secret(self):
        json = self.layer.get_json(self.endpoint+'/secret_1')
        self.assertEquals(json['name'], 'secret 1')
    
    def test_secret_collection(self):
        json = self.layer.get_json(self.endpoint+'?results_per_page='+str(self.model_count))
        self.assertEquals(len(json['objects']), self.model_count)
    
    def test_secret_status(self):
        _json = self.layer.get_json(self.endpoint+'/secret_1')
        self.assertEquals(_json['status_token'], '')
        
        r = self.layer.client.patch(
                self.endpoint+'/secret_1',
                headers={'Content-Type':'application/json'},
                data=json.dumps({'status_token': 'status_2'}))
        self.assertEqual(r.status_code, 200)
        
        _json = self.layer.get_json(self.endpoint+'/secret_1')
        self.assertEquals(_json['status_token'], 'status_2')
    
    def test_secret_severity(self):
        _json = self.layer.get_json(self.endpoint+'/secret_1')
        self.assertEquals(_json['severity_token'], '')
        
        r = self.layer.client.patch(
                self.endpoint+'/secret_1',
                headers={'Content-Type':'application/json'},
                data=json.dumps({'severity_token': 'severity_2'}))
        self.assertEqual(r.status_code, 200)
        
        _json = self.layer.get_json(self.endpoint+'/secret_1')
        self.assertEquals(_json['severity_token'], 'severity_2')
    
class test_suite(object):
    layer = testing.MELLON_API_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonApiSecretsTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
