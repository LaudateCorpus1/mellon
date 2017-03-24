import os.path
import unittest
import zope.testrunner
from zope import component
from mellon_api import testing
from mellon_api.api import IAPISAEndpoints

class MellonApiResourceRegistrationTestCase(unittest.TestCase):
    layer = testing.MELLON_API_RUNTIME_LAYER

    def test_endpoint_registration(self):
        endpoints = component.getUtility(IAPISAEndpoints)
        self.assertIn('authorization-contexts', endpoints.map)


class test_suite(object):
    layer = testing.MELLON_API_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonApiResourceRegistrationTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
