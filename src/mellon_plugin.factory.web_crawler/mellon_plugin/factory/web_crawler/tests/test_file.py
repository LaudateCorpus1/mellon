import os.path
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin

from mellon_plugin.factory.web_crawler.testing import MELLON_FACTORY_EXECUTED_WEB_CRAWLER_LAYER

class MellonScrapyFileProviderTestCase(unittest.TestCase):
    layer = MELLON_FACTORY_EXECUTED_WEB_CRAWLER_LAYER
    sm = component.getSiteManager()
    
    def __init__(self, *args, **kwargs):
        self.layer.verbose = False
        self.layer.debug = False
        super(MellonScrapyFileProviderTestCase, self).__init__(*args, **kwargs)

    def test_mfp(self):
        self.assertIsNotNone(self.layer.get_file_by_name('index.html'))
        self.assertIsNone(self.layer.get_file_by_name('_dummy.html'))

class test_suite(test_suite_mixin):
    layer = MELLON_FACTORY_EXECUTED_WEB_CRAWLER_LAYER
    package = 'mellon_plugin.factory.web_crawler'
    module = 'file'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonScrapyFileProviderTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])