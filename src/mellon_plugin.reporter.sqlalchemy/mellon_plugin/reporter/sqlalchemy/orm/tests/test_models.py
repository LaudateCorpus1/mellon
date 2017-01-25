import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from mellon.testing import MELLON_INTEGRATION_LAYER
import sqlalchemy
from sqlalchemy import event
from sqlalchemy import exc
from sqlalchemy import orm
from sqlalchemy.engine import reflection
from ..models import Base, AuthorizationContext, MellonFile, Snippet, Secret

class MellonORMReporterTestCase(unittest.TestCase):
    layer = MELLON_INTEGRATION_LAYER
    
    debug = False
    
    def setUp(self, *args, **kwargs):
        #http://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
        def _fk_pragma_on_connect(dbapi_con, con_record):
            dbapi_con.execute('pragma foreign_keys=ON')
        
        self.engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=self.debug)
        event.listen(self.engine, 'connect', _fk_pragma_on_connect)
        Base.metadata.create_all(self.engine)
        Session = orm.sessionmaker(bind=self.engine)
        self.session = Session()

    def test_schema(self):
        insp = reflection.Inspector.from_engine(self.engine)
        self.assertTrue(AuthorizationContext.__tablename__ in insp.get_table_names())
    
    def test_foriegn_keys(self):
        auth_context1 = AuthorizationContext(id='auth_id1', name='auth_name1')
        self.session.add(auth_context1)
        self.session.commit()
        
        mfile1 = MellonFile(name='mfile1') #foreign key fail
        self.session.add(mfile1)
        with self.assertRaises(exc.IntegrityError):
            self.session.commit()
        self.session.rollback()
        
        auth_context1.mellon_files = [MellonFile(name='mfile2'), MellonFile(name='mfile3')]
        self.session.add(auth_context1)
        self.session.commit()
        self.assertEquals(len(self.session.dirty), 0)
        
        contexts = self.session.query(AuthorizationContext).all()
        self.assertEquals(contexts[0].id, 'auth_id1')
        
        mfiles = self.session.query(MellonFile).order_by(MellonFile.name).all()
        self.assertEquals(mfiles[0].name, 'mfile2')
        

class test_suite(test_suite_mixin):
    layer = MELLON_INTEGRATION_LAYER
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