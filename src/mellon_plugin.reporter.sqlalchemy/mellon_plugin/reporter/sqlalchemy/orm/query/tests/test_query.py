import os.path
import doctest
import unittest
import zope.testrunner

from zope import component
from .. import ISAInstrumentedAttribute, ISAQuery, ISAOuterJoinQuery
from mellon_plugin.reporter.sqlalchemy.orm.testing import MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
from mellon_plugin.reporter.sqlalchemy.orm import models

class MellonOrmQueryTestCase(unittest.TestCase):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    
    def setUp(self):
        #self.layer.session.begin_nested()
        self.layer.create_complex_model()
        self.layer.session.flush()
    
    def tearDown(self):
        self.layer.session.rollback()
    
    def test_orm_related_models_adder(self):
        rmodel = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.orm_related_models_adder")
        sequence = [models.MellonFile, models.Snippet, models.Secret]
        rmodel.add_sequence(sequence)
        #To test flattened, it won't be possible to measure sequences because the
        #internal graph structure leverages unordered sets.  We'll have to 
        #test using <> on expected index ordering
        
        #simple ones
        self.assertEqual(set(rmodel.flattened(models.MellonFile)[1:]), set(sequence[1:]))
        #re-adding doesn't impact
        rmodel.add_sequence(sequence)
        self.assertEqual(set(rmodel.flattened(models.MellonFile)[1:]), set(sequence[1:]))
        #starting from middle grows outward
        self.assertEqual(set(rmodel.flattened(models.Snippet)[1:]), 
                         set([models.MellonFile, models.Secret]))
        
        #append some items
        rmodel.add_sequence([models.Secret, models.SecretDiscoveryDate])
        self.assertEqual(set(rmodel.flattened(models.MellonFile)[1:]), 
                         set([models.Snippet, models.Secret, models.SecretDiscoveryDate]))
        
        #prepend some other items
        rmodel.add_sequence([models.AuthorizationContext, models.MellonFileAccessContext, models.MellonFile])
        self.assertEqual(set(rmodel.flattened(models.AuthorizationContext)[1:]), 
                         set([models.MellonFileAccessContext, models.MellonFile, models.Snippet, models.Secret, models.SecretDiscoveryDate]))
        self.assertEqual(set(rmodel.flattened(models.MellonFile)[1:]), 
                         set([models.MellonFileAccessContext, models.AuthorizationContext, models.Snippet, models.Secret, models.SecretDiscoveryDate]))
        
        #cylindrical doesn't break stuff
        cylindrical = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.orm_related_models_adder")
        cylindrical.add_sequence([models.MellonFile, models.MellonFile])
        self.assertEqual([m for m in cylindrical.flattened(models.MellonFile)], [models.MellonFile])
    
    def test_core_related_model_registration(self):
        rmodels = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        self.assertIn(models.MellonFile, rmodels.flattened(models.MellonFile))
    
    def test_instrumented_attribute_factory(self):
        with self.assertRaises(TypeError):
            component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.instrumented_attribute",
                    'dummy.id')
        with self.assertRaises(AttributeError):
            component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.instrumented_attribute",
                    'MellonFile.dummy')
        ia = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.instrumented_attribute",
                    'MellonFile.id')
        self.assertTrue(ISAInstrumentedAttribute.providedBy(ia))
    
    def test_query_factory(self):
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        q = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.query",
                    *core_models.flattened(models.MellonFile))
        self.assertTrue(ISAQuery.providedBy(q))
    
    def test_outer_joined_query_factory(self):
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        q = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.Secret)
                    )
        self.assertTrue(ISAOuterJoinQuery.providedBy(q))
        
    def test_basic_query_results(self):
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        core_models.add_sequence([models.Secret, models.Snippet, models.MellonFile])
        #simplest search will be for a secret, it should only return based on the
        #total count of secrets in db (other would return many-to-one results)
        q = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.Secret)
                    )
        self.assertEqual(q.count(), 3)


class test_suite(object):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    
    def __new__(cls):
        suite = unittest.TestSuite()
        def setUpDocTest(test):
            cls.layer.create_complex_model()
            cls.layer.session.flush()
    
        def tearDownDocTest(test):
            cls.layer.session.rollback()
        
        docfiletest = doctest.DocFileSuite('query.txt',
                        package='mellon_plugin.reporter.sqlalchemy.orm.query',
                        setUp=setUpDocTest,
                        tearDown=tearDownDocTest)
        docfiletest.layer = cls.layer
        suite.addTest(docfiletest)
        suite.addTest(unittest.makeSuite(MellonOrmQueryTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])