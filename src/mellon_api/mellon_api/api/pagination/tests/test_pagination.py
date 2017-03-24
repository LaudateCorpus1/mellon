import os.path
import unittest
import zope.testrunner

from mellon_api.api import testing

from zope import component
from .. import IAPIPagination

class MellonAPIPaginationTestCase(unittest.TestCase):
    layer = testing.MELLON_API_RESOURCE_RUNTIME_LAYER
    model_count = 75
    
    def setUp(self):
        self.layer.create_test_resources(count=self.model_count)
    
    def tearDown(self):
        self.layer.reset_test_resources()
    
    def test_request_page(self):
        with self.layer.flask_app.test_request_context('/?offset=5&limit=10'):
            r = component.createObject(u"mellon_api.flask_request")
            page_r = component.createObject(
                    u"mellon_api.api.pagination.page_request_from_request_and_count",
                    r, 10)
            self.assertEqual(page_r.offset, 5)
            self.assertEqual(page_r.limit, 10)
            
            page_r = component.createObject(
                    u"mellon_api.api.pagination.page_request_from_request_and_count",
                    r, 6)
            self.assertEqual(page_r.offset, 5)
            
            page_r = component.createObject(
                    u"mellon_api.api.pagination.page_request_from_request_and_count",
                    r, 5)
            self.assertEqual(page_r.offset, 0)
            
        with self.layer.flask_app.test_request_context('/?offset=-1&limit=10'):
            page_r = component.createObject(
                    u"mellon_api.api.pagination.page_request_from_request_and_count",
                    r, 10)
            self.assertEqual(page_r.offset, 0)
            
        with self.layer.flask_app.test_request_context('/?offset=5&limit=75'):
            r = component.createObject(u"mellon_api.flask_request")
            page_r = component.createObject(
                    u"mellon_api.api.pagination.page_request_from_request_and_count",
                    r, self.model_count)
            self.assertEqual(page_r.offset, 5)
            self.assertEqual(page_r.limit, 51) #request is beyond max_limit

    def test_request_pagination_adapter(self):
        with self.layer.flask_app.test_request_context('/?offset=5&limit=10'):
            r = component.createObject(u"mellon_api.flask_request")
            pag = IAPIPagination(r)
            pag.first = 'test'
            r = component.createObject(u"mellon_api.flask_request")
            pag = IAPIPagination(r)
            self.assertEqual(pag.first, 'test')

    def test_request_pagination_from_count(self):
        with self.layer.flask_app.test_request_context('/test-resources?offset=23&limit=10'):
            r = component.createObject(u"mellon_api.flask_request")
            page = component.createObject(
                    u"mellon_api.api.pagination.pagination_from_request_and_count",
                    r, self.layer.get_resource_count())
            page.first
            self.assertEqual(page._offset_pointer, 0)
            page.last
            self.assertEqual(page._offset_pointer, 69)
            page.next
            self.assertEqual(page._offset_pointer, 33)
            page.prev
            self.assertEqual(page._offset_pointer, 13)
        # illegal offset request default back to 0
        with self.layer.flask_app.test_request_context('/test-resources?offset=100&limit=10'):
            r = component.createObject(u"mellon_api.flask_request")
            page = component.createObject(
                    u"mellon_api.api.pagination.pagination_from_request_and_count",
                    r, self.layer.get_resource_count())
            page.next
            self.assertEqual(page._offset_pointer, 10)
            self.assertEqual(page.prev, None)
        # illegal offset request default back to 0
        with self.layer.flask_app.test_request_context('/test-resources?offset=-100&limit=10'):
            r = component.createObject(u"mellon_api.flask_request")
            page = component.createObject(
                    u"mellon_api.api.pagination.pagination_from_request_and_count",
                    r, self.layer.get_resource_count())
            page.next
            self.assertEqual(page._offset_pointer, 10)
        # offset on last count item
        with self.layer.flask_app.test_request_context('/test-resources?offset=74&limit=10'):
            r = component.createObject(u"mellon_api.flask_request")
            page = component.createObject(
                    u"mellon_api.api.pagination.pagination_from_request_and_count",
                    r, self.layer.get_resource_count())
            self.assertEqual(page.next, None)
        
            

class test_suite(object):
    layer = testing.MELLON_API_RESOURCE_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(MellonAPIPaginationTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])
