import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin

from zope import component
from .. import IORMRelatedModels
from mellon_plugin.reporter.sqlalchemy.orm.testing import MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
from mellon_plugin.reporter.sqlalchemy import orm
from mellon_plugin.reporter.sqlalchemy.orm import models
from mellon_plugin.reporter.sqlalchemy.orm import query

class MellonOrmResultTestCase(unittest.TestCase):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    
    def setUp(self):
        self.layer.create_complex_model()
        self.layer.session.flush()
    
    def tearDown(self):
        self.layer.session.rollback()
    
    def test_basic_query_result_row_column_getter(self):
        core_models = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.mellon_core_related_models")
        core_models.add_sequence([models.Secret, models.Snippet, models.MellonFile])
        #simplest search will be for a secret, it should only return based on the
        #total count of secrets in db (other would return many-to-one results)
        q = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.outer_joined_query",
                    core_models.flattened(models.Secret)
                    )
        mf = component.getUtility(query.ISAResultRowModel).first(orm.ISAMellonFile, q.first())
        self.assertTrue(orm.ISAMellonFile.providedBy(mf))

class test_suite(test_suite_mixin):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    package = 'mellon_plugin.reporter.sqlalchemy.orm.query'
    module = 'result'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonOrmResultTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])