import os.path
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin

import mellon_api
from ..testing import MELLON_API_RUNTIME_LAYER


class MellonApiKwargsTestCase(unittest.TestCase):
    layer = MELLON_API_RUNTIME_LAYER
    
    def test_app(self):
        app = component.getUtility(mellon_api.IFlaskApplication)
        self.assertTrue(mellon_api.IFlaskApplication.providedBy(app))
    
class test_suite(test_suite_mixin):
    layer = MELLON_API_RUNTIME_LAYER
    package = 'mellon_api'
    module = 'app'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonApiKwargsTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])