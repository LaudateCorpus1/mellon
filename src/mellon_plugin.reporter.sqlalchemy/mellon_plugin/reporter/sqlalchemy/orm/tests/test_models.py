import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from sqlalchemy import exc
from sqlalchemy.engine import reflection
from .. import models, interfaces

from ..testing import MELLON_SA_ORM_REPORTER_RUNTIME_LAYER

class MellonORMReporterTestCase(unittest.TestCase):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    
    def test_schema(self):
        insp = reflection.Inspector.from_engine(self.layer.engine)
        self.assertTrue(models.AuthorizationContext.__tablename__ in insp.get_table_names())
    
    def test_models(self):
        auth_context1 = models.AuthorizationContext(id='auth_id1', name='auth_name1')
        self.layer.session.add(auth_context1)
        self.layer.session.commit()
        
        mfile1 = models.MellonFile(name='mfile1') #foreign key fail
        self.layer.session.add(mfile1)
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.commit()
        self.layer.session.rollback()
        
        auth_context1.mellon_files = [models.MellonFile(name='mfile2'), models.MellonFile(name='mfile3')]
        self.layer.session.add(auth_context1)
        self.layer.session.commit()
        self.assertEquals(len(self.layer.session.dirty), 0)
        
        contexts = self.layer.session.query(models.AuthorizationContext).all()
        self.assertEquals(contexts[0].id, 'auth_id1')
        
        #quick test to insure retrieved models provide the correct interface
        self.assertTrue(interfaces.IORMAuthorizationContext.providedBy(contexts[0]))
        
        mfiles = self.layer.session.query(models.MellonFile).order_by(models.MellonFile.name).all()
        self.assertEquals(mfiles[0].name, 'mfile2')
    
    def test_model_factory(self):
        pass

class test_suite(test_suite_mixin):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    package = 'mellon_plugin.reporter.sqlalchemy.orm'
    module = 'models'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonORMReporterTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])