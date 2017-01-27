import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from sqlalchemy import exc
from sqlalchemy.engine import reflection
from .. import models
from .. import interfaces as i

from zope import component
from io import StringIO
from datetime import datetime
from ..testing import MELLON_SA_ORM_REPORTER_RUNTIME_LAYER

class MellonORMReporterTestCase(unittest.TestCase):
    layer = MELLON_SA_ORM_REPORTER_RUNTIME_LAYER
    
    def tearDown(self):
        self.layer.session.rollback()
    
    def test_schema(self):
        insp = reflection.Inspector.from_engine(self.layer.engine)
        self.assertTrue(models.AuthorizationContext.__tablename__ in insp.get_table_names())
    
    def test_model_MellonFile(self):
        mfile1 = models.MellonFile(name='mfile1')
        self.layer.session.add(mfile1)
        
        mfile1 = self.layer.session.query(models.MellonFile).first()
        self.assertEquals(mfile1.name, 'mfile1')
    
    def test_model_Snippet(self):
        snippet1 = models.Snippet(name='snippet_name1') #foreign key fail
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.add(snippet1)
            self.layer.session.flush()
        self.layer.session.rollback()
        
        mfile1 = models.MellonFile(name='mfile1')
        mfile1.snippets = [snippet1]
        self.layer.session.add(mfile1)
        
        snippet1 = self.layer.session.query(models.Snippet).first()
        self.assertEquals(snippet1.id, 1)
    
    def test_model_Secret(self):
        mfile1 = models.MellonFile(name='mfile1')
        snippet1 = models.Snippet(id=1,name='snippet_name1')
        secret1 = models.Secret(id='1',name='secret_name1')
        mfile1.snippets = [snippet1]
        snippet1.secrets = [secret1]
        self.layer.session.add(mfile1)
        
        secret1 = self.layer.session.query(models.Secret).first()
        self.assertEquals(secret1.id, '1')
    
    def test_model_SecretDiscoveryDate(self):
        now = datetime.now()
        
        #invalid entries won't go
        disc_date_model1 = models.SecretDiscoveryDate(datetime=now) #doesn't have an assigned secret
        self.layer.session.add(disc_date_model1)
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.query(models.SecretDiscoveryDate).all()
        self.layer.session.rollback()
        disc_date_model1 = models.SecretDiscoveryDate(datetime=now, secret_id='bad')
        self.layer.session.add(disc_date_model1)
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.query(models.SecretDiscoveryDate).all()
        self.layer.session.rollback()
        
        #good entries work as expected
        mfile1 = models.MellonFile(name='mfile1')
        snippet1 = models.Snippet(id=1,name='snippet_name1')
        secret1 = models.Secret(id='1',name='secret_name1')
        discovery1 = models.SecretDiscoveryDate(datetime=now)
        mfile1.snippets = [snippet1]
        snippet1.secrets = [secret1]
        secret1.secret_discovery_dates = [discovery1]
        self.layer.session.add(mfile1)
        
        discovery1 = self.layer.session.query(models.SecretDiscoveryDate).first()
        self.assertEquals(discovery1.secret_id, secret1.id)
        self.assertEquals(discovery1.datetime, now)
        
        #duplicate entries won't go
        discovery2 = models.SecretDiscoveryDate(datetime=now)
        secret1.secret_discovery_dates = [discovery1, discovery2]
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.query(models.SecretDiscoveryDate).all()
        self.layer.session.rollback()
        
    def test_model_AuthorizationContext(self):
        auth_context1 = models.AuthorizationContext(id='auth_id1', name='auth_name1')
        self.layer.session.add(auth_context1)
        
        auth_context1.mellon_files = [models.MellonFile(name='mfile2'), models.MellonFile(name='mfile3')]
        self.layer.session.add(auth_context1)

        auth_context1 = self.layer.session.query(models.AuthorizationContext).first()
        self.assertEquals(auth_context1.id, 'auth_id1')
    
    def test_model_factory(self):
        auth_context_model = models.OrmModelFromMellonProvider(\
                                component.createObject(
                                    u"mellon.authorization_context",
                                    id='test_id'))
        self.assertTrue(i.ISAAuthorizationContext.providedBy(auth_context_model))
        
        mfile_model = models.OrmModelFromMellonProvider(\
                                component.createObject(
                                    u"mellon.unicode_file_from_stream",
                                    StringIO(u'test unicode file 1'),
                                    self.layer.app.get_config()))
        self.assertTrue(i.ISAMellonFile.providedBy(mfile_model))
        
        snippet_model = models.OrmModelFromMellonProvider(\
                                component.createObject(u"mellon.unicode_snippet"))
        self.assertTrue(i.ISASnippet.providedBy(snippet_model))
        
        secret_model = models.OrmModelFromMellonProvider(\
                                component.createObject(u"mellon.secret", 
                                    'a secret', 
                                    component.createObject(u"mellon.unicode_snippet")))
        self.assertTrue(i.ISASecret.providedBy(secret_model))

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