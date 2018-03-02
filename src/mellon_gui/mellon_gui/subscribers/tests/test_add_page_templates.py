import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from pyramid import testing
from mellon_gui import populate_pyramid_config

class MellonPTTestCase(unittest.TestCase):
    
    def setUp(self):
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        populate_pyramid_config(self.config)

    def tearDown(self):
        testing.tearDown()
    
    def test_main_page_template_availability(self):
        from pyramid.events import BeforeRender
        brender = BeforeRender({})
        self.config.registry.notify(brender)
        self.assertIn('main', brender)
    
    
class test_suite(test_suite_mixin):
    package = 'mellon_gui.subscribers'
    module = 'add_page_templates'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonPTTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])