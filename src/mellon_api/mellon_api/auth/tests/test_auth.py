import os.path
import unittest
import zope.testrunner

import time
import json
from zope import component
import mellon_api
from ..auth import api_authentication_preprocessor
from mellon_api.sa import ISASession
from .. import IUserPasswordAuthenticationManager
from ..testing import MELLON_API_AUTH_RUNTIME_LAYER


from sparc.logging import logging
logger = logging.getLogger(__name__)

class MellonApiAuthTestCase(unittest.TestCase):
    layer = MELLON_API_AUTH_RUNTIME_LAYER
    model_count = 1
    
    def setUp(self):
        self.endpoint = "/api/secrets"
        self.layer.create_full_model(count=self.model_count)
        self.layer.session.flush()
        
        self.session = component.getUtility(ISASession)
        self.manager = IUserPasswordAuthenticationManager(self.session)
        
    
    def tearDown(self):
        self.layer.session.rollback()
        self.session.rollback()
    
    def login(self, username, password):
        r = self.layer.client.post('/api/login', data={'username': username,
                                             'password': password})
        return json.loads(r.get_data(as_text=True))['token'] if r.status_code == 200 else None
    
    def test_preprocessor_injection(self):
        pp = component.getUtility(mellon_api.IFlaskRestApiPreprocessors, name='mellon_api.preprocessors_global')
        self.assertEquals(pp['GET_SINGLE'][0], api_authentication_preprocessor)
    
    def test_basic_auth_provider(self):
        self.manager.create('user1', 'password1')
        r = self.layer.get_response('/api/secrets')
        self.assertEqual(r.status_code, 401)
        json = self.layer.get_json('/api/secrets')
        self.assertEqual(json, {'message': 'Not Authorized'})
        
        basicauth = ('user1', 'password1')
        r = self.layer.get_response('/api/secrets', basicauth=basicauth)
        self.assertEqual(r.status_code, 200)
        
        basicauth = ('invalid_user', '')
        r = self.layer.get_response('/api/secrets', basicauth=basicauth)
        self.assertEqual(r.status_code, 401)
        
        basicauth = ('user1', 'invalid_password')
        r = self.layer.get_response('/api/secrets', basicauth=basicauth)
        self.assertEqual(r.status_code, 401)

    def test_token_login(self):
        self.manager.create('user1', 'password1')
        token = self.login('user1', 'password1')
        self.assertIsNotNone(token)
    
    def test_token_resource_access(self):
        self.manager.create('user1', 'password1')
        token = self.login('user1', 'password1')
        r = self.layer.get_response('/api/secrets', basicauth=(token,''))
        self.assertEqual(r.status_code, 200)
        time.sleep(self.layer.token_lifespan+1)
        r = self.layer.get_response('/api/secrets', basicauth=(token,''))
        self.assertEqual(r.status_code, 401)
        r = self.layer.get_response('/api/secrets', basicauth=('bad_signature',''))
        self.assertEqual(r.status_code, 401)
        
        
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
