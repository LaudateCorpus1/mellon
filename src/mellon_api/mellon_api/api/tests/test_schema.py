import os.path
import unittest
import zope.testrunner

from mellon_api import testing
from mellon_plugin.reporter.sqlalchemy.orm import models as orm_models
from .. import schema

class MellonSchemaAuthorizationContextTestCase(unittest.TestCase):
    layer = testing.MELLON_API_RUNTIME_LAYER
    model_count = 1
    
    def test_schema_authorization_context(self):
        schema_ac = schema.AuthorizationContextSchema()
        model_ac = orm_models.AuthorizationContext(
                                    id='ac_1',
                                    name='ac name',
                                    description='ac description')
        container = schema_ac.dump(model_ac).data
        self.assertEqual(container['data']['id'], 'ac_1')
        self.assertEqual(container['data']['attributes']['description'], 'ac description')
        self.assertEqual(container['data']['attributes']['name'], 'ac name')
    
class test_suite(object):
    layer = testing.MELLON_API_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonSchemaAuthorizationContextTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
