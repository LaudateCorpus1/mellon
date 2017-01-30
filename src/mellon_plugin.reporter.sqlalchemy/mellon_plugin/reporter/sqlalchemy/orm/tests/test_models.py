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
    
    def setUp(self):
        #create the empty-string authorization context
        self.layer.session.add(models.AuthorizationContext())
        self.layer.session.flush()

    def tearDown(self):
        self.layer.session.rollback()
    
    def test_schema(self):
        insp = reflection.Inspector.from_engine(self.layer.engine)
        self.assertTrue(models.AuthorizationContext.__tablename__ in insp.get_table_names())
        
    def test_model_AuthorizationContext(self):
        auth_context1 = models.AuthorizationContext(id='auth_id1', name='auth_name1')
        self.layer.session.add(auth_context1)
        self.layer.session.flush()
        
        self.layer.session.add(
                models.MellonFile(name='mfile2',authorization_context_id='auth_id1'), 
                models.MellonFile(name='mfile3', authorization_context_id='auth_id1')
                )
        self.layer.session.flush()

        auth_context1 = self.layer.session.query(models.AuthorizationContext).\
                            filter(
                                models.AuthorizationContext.id == 'auth_id1').\
                                first()
        self.assertEquals(auth_context1.id, 'auth_id1')
    
    def test_model_MellonFile(self):
        mfile1 = models.MellonFile(name='mfile1')
        self.layer.session.add(mfile1)
        
        mfile1 = self.layer.session.query(models.MellonFile).first()
        self.assertEquals(mfile1.name, 'mfile1')
    
    def test_model_MellonFile_uniqueness_1(self):
        #can't add 2 files with same name and auth context
        mfile1 = models.MellonFile(name='mfile')
        self.layer.session.add(mfile1)
        mfile2 = models.MellonFile(name='mfile')
        self.layer.session.add(mfile2)
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.flush()
    
    def test_model_MellonFile_uniqueness_2(self):
        #can't update a file to a conflicting state
        mfile1 = models.MellonFile(name='mfile')
        self.layer.session.add(mfile1)
        mfile2 = models.MellonFile(name='mfileA')
        self.layer.session.add(mfile2)
        self.layer.session.flush()
        mfile2.name = 'mfile'
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.flush()
        
    
    def test_model_Snippet_1(self):
        snippet1 = models.Snippet(name='snippet_name1') #foreign key fail
        self.layer.session.add(snippet1)
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.flush()
    
    def test_model_Snippet_2(self):
        mfile1 = models.MellonFile(name='mfile1')
        self.layer.session.add(mfile1)
        self.layer.session.flush()
        
        snippet1 = models.Snippet(name='snippet_name1')
        snippet1.mellon_file_id = mfile1.id
        self.layer.session.add(snippet1)
        snippet1 = self.layer.session.query(models.Snippet).first()
        self.assertEquals(snippet1.id, 1)
    
    def test_model_Secret(self):
        mfile1 = models.MellonFile(name='mfile1')
        self.layer.session.add(mfile1)
        self.layer.session.flush()
        snippet1 = models.Snippet(id=1,name='snippet_name1', mellon_file_id=mfile1.id)
        self.layer.session.add(snippet1)
        self.layer.session.flush()
        secret1 = models.Secret(id='1',name='secret_name1',snippet_id=snippet1.id)
        self.layer.session.add(secret1)
        self.layer.session.flush()
        
        secret1 = self.layer.session.query(models.Secret).first()
        self.assertEquals(secret1.id, '1')
    
    def test_model_DiscoveryDate_1(self):
        #invalid entries won't go (foreign key fail)
        now = datetime.now()
        disc_date_model1 = models.SecretDiscoveryDate(datetime=now) #doesn't have an assigned secret
        self.layer.session.add(disc_date_model1)
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.query(models.SecretDiscoveryDate).all()
    
    def test_model_DiscoveryDate_2(self):
        #invalid entries won't go (foreign key fail)
        now = datetime.now()
        disc_date_model1 = models.SecretDiscoveryDate(datetime=now, secret_id='bad')
        self.layer.session.add(disc_date_model1)
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.query(models.SecretDiscoveryDate).all()
    
    def test_model_DiscoveryDate_3(self):
        now = datetime.now()
        #good entries work as expected
        mfile1 = models.MellonFile(name='mfile1')
        self.layer.session.add(mfile1)
        self.layer.session.flush()
        snippet1 = models.Snippet(id=1,name='snippet_name1',mellon_file_id=mfile1.id)
        self.layer.session.add(snippet1)
        self.layer.session.flush()
        secret1 = models.Secret(id='1',name='secret_name1',snippet_id=snippet1.id)
        self.layer.session.add(secret1)
        self.layer.session.flush()
        discovery1 = models.SecretDiscoveryDate(datetime=now,secret_id=secret1.id)
        self.layer.session.add(discovery1)
        self.layer.session.flush()
        
        discovery1 = self.layer.session.query(models.SecretDiscoveryDate).first()
        self.assertEquals(discovery1.secret_id, secret1.id)
        self.assertEquals(discovery1.datetime, now)
        
        #duplicates fail
        discovery2 = models.SecretDiscoveryDate(datetime=now,secret_id=secret1.id)
        self.layer.session.add(discovery2)
        with self.assertRaises(exc.IntegrityError):
            self.layer.session.query(models.SecretDiscoveryDate).all()
    
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