import os.path
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin

import mellon_api
from ..testing import MELLON_API_RUNTIME_LAYER


class MellonApiwargsTestCase(unittest.TestCase):
    layer = MELLON_API_RUNTIME_LAYER
    
    def test_app(self):
        eve_app = component.getUtility(mellon_api.IEveApplication)
        self.assertTrue(mellon_api.IEveApplication.providedBy(eve_app))
    
    def test_kwargs(self):
        kwargs = component.getUtility(mellon_api.IEveApplicationKwargs).kwargs
        self.assertTrue(isinstance(kwargs, dict))


class test_suite(test_suite_mixin):
    layer = MELLON_API_RUNTIME_LAYER
    package = 'mellon_api'
    module = 'app'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonApiwargsTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])