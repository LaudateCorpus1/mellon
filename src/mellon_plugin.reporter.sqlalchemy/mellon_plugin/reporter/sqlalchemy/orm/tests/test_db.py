import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin

from mellon.reporters.memory.memory import report as memory_report
from mellon.sniffers.test.test import reset_test_sniffer
from ..testing import MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
from .. import models
from zope import event
import mellon

from mellon.reporters.memory.memory import reset_report

class MellonOrmReporterTestCase(unittest.TestCase):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    
    def setUp(self):
        #self.layer.session.begin_nested()
        self.layer.app.go()
        self.layer.session.flush()
    
    def tearDown(self):
        self.layer.session.rollback()
        reset_report()
        reset_test_sniffer()
    
    def test_reporter(self):
        # now check orm
        self.assertEqual(len(self.layer.session.query(models.AuthorizationContext).all()), 1)
        self.assertEqual(len(self.layer.session.query(models.MellonFile).all()), 2)
        self.assertEqual(len(self.layer.session.query(models.MellonFileAccessContext).all()), 2)
        self.assertEqual(len(self.layer.session.query(models.Snippet).all()), 2)
        self.assertEqual(len(self.layer.session.query(models.Secret).all()), 2)
        self.assertEqual(len(self.layer.session.query(models.SecretDiscoveryDate).all()), 2)
    
    def test_repeated_secret(self):
        self.assertEqual(len(self.layer.session.query(models.Secret).all()), 2)
        _tripper = False
        reset_test_sniffer()
        for secret in memory_report:
            snippet = secret.__parent__
            event.notify(mellon.events.SnippetAvailableForSecretsSniffEvent(snippet))
            _tripper = True
        self.assertTrue(_tripper) #make sure loop ran ok
        self.assertEqual(len(self.layer.session.query(models.Secret).all()), 2) #no new secrets.
        
        #now we'll just verify that the events were indeed ok by wiping the DB and trying again
        for secret_discovery_date in self.layer.session.query(models.SecretDiscoveryDate).all():
            self.layer.session.delete(secret_discovery_date)
        self.assertEqual(len(self.layer.session.query(models.SecretDiscoveryDate).all()), 0)
        for secret_model in self.layer.session.query(models.Secret).all():
            self.layer.session.delete(secret_model)
        self.assertEqual(len(self.layer.session.query(models.Secret).all()), 0)
        reset_test_sniffer()
        for secret in memory_report:
            snippet = secret.__parent__
            event.notify(mellon.events.SnippetAvailableForSecretsSniffEvent(snippet))
        self.assertEqual(len(self.layer.session.query(models.Secret).all()), 2) #the entries should be added this time around
        

class test_suite(test_suite_mixin):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    package = 'mellon_plugin.reporter.sqlalchemy.orm'
    module = 'db'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonOrmReporterTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])