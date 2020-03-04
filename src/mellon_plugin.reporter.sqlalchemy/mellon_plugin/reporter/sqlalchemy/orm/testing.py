from datetime import datetime as dt
from os import remove
from os import path
from mellon.testing import MellonApplicationRuntimeLayer
from mellon.reporters.memory.memory import reset_report
from sqlalchemy import create_engine, event
import mellon_plugin.reporter.sqlalchemy.orm
from datetime import datetime
from .db import get_session
from . import models

class MellonOrmRuntimeReporterLayer(MellonApplicationRuntimeLayer):
    
    sqlite_file = 'mellon.db'
    #sqlite_file = ':memory:'
    dsn = 'sqlite:///' + sqlite_file
    
    def create_engine(self):
        engine = create_engine(self.dsn, echo=self.debug)
        
        #http://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
        def _fk_pragma_on_connect(dbapi_con, con_record):
            dbapi_con.execute('pragma foreign_keys=ON')
        event.listen(engine, 'connect', _fk_pragma_on_connect)
        
        return engine
    
    def create_full_model(self, count=1):
        """Returns a list of dicts (or a single dict) whose keys are Model names, and whose values are the related models"""
        _return = []
        for i in range(count):
            num = str(i+1)
            auth_context = models.AuthorizationContext(id='authorization_context_'+num,name='authorization context '+num)
            self.session.add(auth_context)
            self.session.flush()
            mellon_file = models.MellonFile(id='mellon file '+num)
            self.session.add(mellon_file)
            self.session.flush()
            access_context = models.MellonFileAccessContext(
                                    mellon_file_id=mellon_file.id,
                                    authorization_context_id=auth_context.id)
            self.session.add(access_context)
            self.session.flush()
            snippet = models.Snippet(name='snippet '+num, mellon_file_id=mellon_file.id)
            self.session.add(snippet)
            self.session.flush()
            now = datetime.now()
            secret = models.Secret(id='secret_'+num,name='secret '+num,snippet_id=snippet.id, initial_discovery_datetime=now)
            self.session.add(secret)
            self.session.flush()
            discovery_date = models.SecretDiscoveryDate(secret_id=secret.id, datetime=now)
            self.session.add(secret)
            self.session.flush()
            _return.append({'AuthorizationContext': auth_context,
                'MellonFile': mellon_file,
                'MellonFileAccessContext': access_context,
                'Snippet': snippet,
                'Secret': secret,
                'SecretDiscoveryDate': discovery_date})
        
        return _return if len(_return) > 1 else _return[0]
    
    def create_complex_model(self):
        auth_contexts = []
        for num in range(1,3):
            auth_context = models.AuthorizationContext(id='authorization_context_{}'.format(num),name='authorization context {}'.format(num))
            auth_contexts.append(auth_context)
            self.session.add(auth_context)
            self.session.flush()
        
        mellon_files = []
        for num in range(1,11):
            mellon_file = models.MellonFile(id='mellon_file_{}'.format(num))
            mellon_files.append(mellon_file)
            self.session.add(mellon_file)
            self.session.flush()
        
        access_context_1 = models.MellonFileAccessContext(
                                mellon_file_id='mellon_file_1',
                                authorization_context_id='authorization_context_1')
        self.session.add(access_context_1)
        access_context_2 = models.MellonFileAccessContext(
                                mellon_file_id='mellon_file_1',
                                authorization_context_id='authorization_context_2')
        self.session.add(access_context_2)
        access_context_3 = models.MellonFileAccessContext(
                                mellon_file_id='mellon_file_2',
                                authorization_context_id='authorization_context_2')
        self.session.add(access_context_3)
        self.session.flush()
        
        snippets_text = []
        for num in range(1,11):
            snippet = models.Snippet(
                        name='snippet {} for unicode mellon file {}'.format(num, 'mellon_file_1'),
                        data_text='data for snippet sequence {}'.format(num),
                        mellon_file_id='mellon_file_1')
            snippets_text.append(snippet)
            self.session.add(snippet)
            self.session.flush()
        
        snippets_bytes = []
        for num in range(1,1024):
            snippet = models.Snippet(
                        name='snippet {} for byte mellon file {}'.format(num, 'mellon_file_2'),
                        data_blob=bytes('data for snippet sequence {}'.format(num), 'latin-1'),
                        mellon_file_id='mellon_file_2')
            snippets_bytes.append(snippet)
            self.session.add(snippet)
            self.session.flush()
        
        #Secret 1
        disc_dates = []
        for i in range(5)[::-1]:
            disc_dates.append(dt(2017,4,25-i))
        
        secret_1 = models.Secret(
                    id='secret_1',
                    name='this is a found secret 1',
                    snippet_id=snippets_text[3].id,
                    initial_discovery_datetime=disc_dates[0])
        self.session.add(secret_1)
        self.session.flush()
        
        for _dt in disc_dates[::-1]:
            disc_date = models.SecretDiscoveryDate(
                    secret_id=secret_1.id,
                    datetime=_dt)
            self.session.add(disc_date)
            self.session.flush()
        
        #Secret 2
        disc_dates = []
        for i in range(5)[::-1]:
            disc_dates.append(dt(2016,7,9-i))
        
        secret_2 = models.Secret(
                    id='secret_2',
                    name='this is a found secret 2',
                    snippet_id=snippets_bytes[366].id,
                    initial_discovery_datetime=disc_dates[0])
        self.session.add(secret_2)
        self.session.flush()
        
        for _dt in disc_dates[::-1]:
            disc_date = models.SecretDiscoveryDate(
                    secret_id=secret_2.id,
                    datetime=_dt)
            self.session.add(disc_date)
            self.session.flush()
        
        #Secret 3
        disc_dates = []
        for i in range(5)[::-1]:
            disc_dates.append(dt(2015,4,13-i))
        
        secret_3 = models.Secret(
                    id='secret_3',
                    name='this is a found secret 3',
                    snippet_id=snippets_bytes[425].id,
                    initial_discovery_datetime=disc_dates[0])
        self.session.add(secret_3)
        self.session.flush()
        
        for _dt in disc_dates[::-1]:
            disc_date = models.SecretDiscoveryDate(
                    secret_id=secret_3.id,
                    datetime=_dt)
            self.session.add(disc_date)
            self.session.flush()
        
    def remove_sqlite_file(self):
        if path.isfile(self.sqlite_file):
            remove(self.sqlite_file)
    
    def get_query_str(self, q):
        from sqlalchemy.dialects import sqlite
        return str(q.statement.compile(dialect=sqlite.dialect()))
    
    def setUp(self, config=None):
        _config = \
            {
             'SQLAlchemyORMReporter':
                {'SQLAlchemyReporter':
                    {'SQLAlchemyEngine':
                        {'dsn': 'sqlite:///:memory:'},
                     }
                 },
             'MellonFileProviderFactory':
                {'name': 'mellon.factories.test.file_provider_for_testing'},
             'MellonSnippet':
                {
                 'lines_increment': 2,
                 'lines_coverage': 5,
                 'bytes_read_size': 512000,
                 'bytes_increment': 7,
                 'bytes_coverage': 8
                },
             'ZopeComponentConfiguration':
                {
                 'zcml': [ {'package': 'mellon_plugin.reporter.sqlalchemy.orm', 'file': 'ftesting.zcml'}]
                }
            }
        if config:
            _config.update(config)
        self.config = _config
        super(MellonOrmRuntimeReporterLayer, self).setUp()
        # We're gonna monkey-patch the default engine to make sure FK checks operate
        self.remove_sqlite_file() #garbage collect
        self.engine = self.create_engine()
        mellon_plugin.reporter.sqlalchemy.orm.db._Engine = self.engine
        mellon_plugin.reporter.sqlalchemy.orm.db._Commit = False # allow tearDown rollbacks
        self.session = get_session()
    
    def tearDown(self):
        self.remove_sqlite_file()
        reset_report()
        # expire the db engine/session globals.
        mellon_plugin.reporter.sqlalchemy.orm.db._session = False
        mellon_plugin.reporter.sqlalchemy.orm.db._Session = False
        mellon_plugin.reporter.sqlalchemy.orm.db._Engine = False
        super(MellonOrmRuntimeReporterLayer, self).tearDown()
MELLON_SA_ORM_REPORTER_RUNTIME_LAYER = MellonOrmRuntimeReporterLayer(mellon_plugin.reporter.sqlalchemy.orm)


