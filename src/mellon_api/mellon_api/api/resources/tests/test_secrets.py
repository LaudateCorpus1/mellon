import os.path
import unittest
import zope.testrunner

from mellon_api.sa import testing

class MellonApiwargsTestCase(unittest.TestCase):
    layer = testing.MELLON_API_SA_EXECUTED_LAYER
    
    def setUp(self):
        from ..secrets import ns_secrets, route
        self.endpoint = "{}{}".format(ns_secrets.name, route)
    
    def test_secret(self):
        pass
    
    def test_secret_collection(self):
        r = self.layer.client.get(self.endpoint)
        self.assertEquals(len(r.data), self.layer.model_count)
    
class test_suite(object):
    layer = testing.MELLON_API_SA_EXECUTED_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonApiwargsTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
