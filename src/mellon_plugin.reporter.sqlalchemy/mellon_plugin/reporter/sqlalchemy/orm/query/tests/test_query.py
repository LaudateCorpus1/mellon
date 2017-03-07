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
    
    def test_orm_related_model(self):
        rmodel = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.orm_related_models")
        self.assertEqual(rmodel.models(), ())
        #start
        rmodel.inject(models.Secret)
        self.assertEqual(rmodel.models(), (models.Secret,))
        #append
        rmodel.inject(models.Snippet, models.Secret)
        self.assertEqual(rmodel.models(), (models.Secret,models.Snippet))
        #inject
        rmodel.inject(models.SecretDiscoveryDate, models.Secret)
        self.assertEqual(rmodel.models(), (models.Secret,models.SecretDiscoveryDate,models.Snippet))
        #init
        rmodel.initialize([models.MellonFile, models.AuthorizationContext])
        self.assertEqual(rmodel.models(), (models.MellonFile, models.AuthorizationContext))
        
    
    def test_core_related_model_registration(self):
        rmodels = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        self.assertIn(models.MellonFile, rmodels.models())
    
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
                    *core_models.models())
        self.assertTrue(ISAQuery.providedBy(q))
    
    def test_outer_joined_query_factory(self):
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        q = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    models.Secret,
                    core_models.models()
                    )
        self.assertTrue(ISAOuterJoinQuery.providedBy(q))
        
    def test_basic_query_results(self):
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        core_models.initialize([models.Secret, models.Snippet, models.MellonFile])
        #simplest search will be for a secret, it should only return based on the
        #total count of secrets in db (other would return many-to-one results)
        q = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    models.Secret,
                    core_models.models()
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