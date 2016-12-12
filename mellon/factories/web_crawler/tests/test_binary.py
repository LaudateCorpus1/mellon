import os.path
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin

import mellon
from mellon.factories.web_crawler.testing import MELLON_FACTORY_EXECUTED_WEB_CRAWLER_LAYER

class MellonScrapyResponseBinaryTestCase(unittest.TestCase):
    layer = MELLON_FACTORY_EXECUTED_WEB_CRAWLER_LAYER
    sm = component.getSiteManager()
    
    def __init__(self, *args, **kwargs):
        self.layer.verbose = False
        self.layer.debug = False
        super(MellonScrapyResponseBinaryTestCase, self).__init__(*args, **kwargs)

    def test_binary_checker(self):
        item = self.layer.get_item_by_name('file.bin')
        self.assertTrue(mellon.IBinaryChecker(item['response']).check())
        item = self.layer.get_item_by_name('index.html')
        self.assertFalse(mellon.IBinaryChecker(item['response']).check())

class test_suite(test_suite_mixin):
    layer = MELLON_FACTORY_EXECUTED_WEB_CRAWLER_LAYER
    package = 'mellon.factories.web_crawler'
    module = 'binary'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonScrapyResponseBinaryTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])