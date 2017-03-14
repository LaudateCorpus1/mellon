import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin

from zope import component
from .. import ISAModelFilterExpression, ISAModelFilterExpressionGroup, ISAConjunction
from .. import ISAExpression
from mellon_plugin.reporter.sqlalchemy.orm.testing import MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
from mellon_plugin.reporter.sqlalchemy.orm import models

class MellonOrmFilterTestCase(unittest.TestCase):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    
    def setUp(self):
        #self.layer.session.begin_nested()
        self.layer.create_complex_model()
        self.layer.session.flush()
    
    def tearDown(self):
        self.layer.session.rollback()
    

    def test_filter_expression_factory(self):
        e = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'model_file_1')
        self.assertTrue(ISAModelFilterExpression.providedBy(e))
        self.assertEqual(e.attribute, models.MellonFile.id)
        self.assertEqual(e.condition, '==')
        self.assertEqual(e.value, 'model_file_1')
    
    def test_filter_sa_expression_adapter(self):
        e = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'model_file_1')
        self.assertTrue(ISAExpression.providedBy(ISAExpression(e)))

    def test_filter_expression_group_factory(self):
        e1 = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'model_file_1')
        eg = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'AND', set([e1]))
        self.assertTrue(ISAModelFilterExpressionGroup.providedBy(eg))
        self.assertEqual(eg.conjunction, 'AND')
        self.assertEqual(eg.expressions, set([e1]))
    
    def test_filter_expression_group_recurse(self):
        e1 = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'model_file_1')
        e2 = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.Secret.name, '!=', 'dummy')
        eg1 = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'AND', set([e1]))
        eg2 = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'OR', set([e2, eg1])) #assignment is the test
        self.assertEqual(eg2.expressions, set([e2, eg1]))
        
    def test_filter_expression_group_conjunction_adapter(self):
        e1 = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'model_file_1')
        e2 = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.Secret.name, '!=', 'dummy')
        eg1 = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'AND', set([e1]))
        eg2 = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'OR', set([e2, eg1])) #assignment is the test
        self.assertTrue(ISAConjunction.providedBy(ISAConjunction(eg1)))
        self.assertTrue(ISAConjunction.providedBy(ISAConjunction(eg2)))
    
    def test_filter_simple(self):
        e1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'mellon_file_1')
        eg1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'AND', set([e1]))
        
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        q = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.Secret))
        q = q.filter(ISAConjunction(eg1))
        self.assertEqual(q.count(), 1) #without filter, would have been 3
        self.assertEqual(q.first()[0].name, 'this is a found secret 1')
        self.assertEqual(q.first()[2].id, 'mellon_file_1')
    
    def test_filter_level_1_or(self):
        e1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'mellon_file_1')
        e2 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'mellon_file_2')
        eg1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'OR', set([e1, e2]))
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        q = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.Secret))
        self.assertEqual(q.filter(ISAConjunction(eg1)).count(), 3) 
    
    def test_filter_level_1_or_complex(self):
        e1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'mellon_file_1')
        e2 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.Secret.id, 'is not null')
        eg1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'OR', set([e1, e2]))
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        q = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.MellonFile))
        self.assertEqual(q.filter(ISAConjunction(eg1)).count(), 12) #10 snippets from file 1 + 2 secrets from file 2
    
    def test_filter_level_1_and(self):
        e1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'mellon_file_1')
        e2 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'mellon_file_2')
        eg1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'AND', set([e1, e2]))
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        q = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.Secret))
        self.assertEqual(q.filter(ISAConjunction(eg1)).count(), 0) 
    
    def test_filter_level_1_and_complex(self):
        e1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '!=', 'mellon_file_1')
        e2 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '!=', 'mellon_file_2')
        eg1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'AND', set([e1, e2]))
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        q = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.MellonFile))
        self.assertEqual(q.filter(ISAConjunction(eg1)).count(), 8)

    def test_filter_level_2_and_or(self):
        """
        AuthorizationContext
        AND
         - secret.id is not null
         - OR
           - mellonfile.name == mellon_file_1
           - mellonfile.name == mellon_file_3
        """
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_auth_context_related_models")
        q = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.AuthorizationContext))
        
        e21 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'mellon_file_1')
        e22 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.MellonFile.id, '==', 'mellon_file_3')
        eg2 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'OR', set([e21, e22]))
        
        e11 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    models.Secret.id, 'is not null')
        eg1 = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
                    'AND', set([e11, eg2]))
        self.assertEqual(q.filter(ISAConjunction(eg1)).count(), 2) #matches 2 auth_context on a single secret

    def test_filter_expression_group_container_converter(self):
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_auth_context_related_models")
        q = component.createObject(u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.AuthorizationContext))
        cont = {'conjunction': 'and',
                'expressions':
                    [{'attribute':'Secret.id', 'condition':'is not null'},
                     {'conjunction': 'or',
                      'expressions':
                            [{'attribute':'MellonFile.id', 'condition':'==', 'value':'mellon_file_1'},
                             {'attribute':'MellonFile.id', 'condition':'==', 'value':'mellon_file_3'}
                             ]
                      }
                    ]
                }
        eg = component.createObject(
                u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group_from_container",
                cont)
        self.assertEqual(q.filter(ISAConjunction(eg)).count(), 2) #matches 2 auth_context on a single secret



class test_suite(test_suite_mixin):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    package = 'mellon_plugin.reporter.sqlalchemy.orm.query'
    module = 'filter'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonOrmFilterTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])