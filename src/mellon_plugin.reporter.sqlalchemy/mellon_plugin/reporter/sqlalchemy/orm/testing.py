from mellon.testing import MellonApplicationRuntimeLayer
from mellon.reporters.memory.memory import reset_report
from sqlalchemy import create_engine, event
import mellon_plugin.reporter.sqlalchemy.orm
from datetime import datetime
from .db import get_session
from . import models

class MellonOrmRuntimeReporterLayer(MellonApplicationRuntimeLayer):
    
    def create_engine(self):
        #http://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
        def _fk_pragma_on_connect(dbapi_con, con_record):
            dbapi_con.execute('pragma foreign_keys=ON')
        engine = create_engine('sqlite:///:memory:', echo=self.debug)
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
            mellon_file = models.MellonFile(name='mellon file '+num, authorization_context_id=auth_context.id)
            self.session.add(mellon_file)
            self.session.flush()
            snippet = models.Snippet(name='snippet '+num, mellon_file_id=mellon_file.id)
            self.session.add(snippet)
            self.session.flush()
            secret = models.Secret(id='secret_'+num,name='secret '+num,snippet_id=snippet.id)
            self.session.add(secret)
            self.session.flush()
            discovery_date = models.SecretDiscoveryDate(secret_id=secret.id, datetime=datetime.now())
            self.session.add(secret)
            self.session.flush()
            _return.append({'AuthorizationContext': auth_context,
                'MellonFile': mellon_file,
                'Snippet': snippet,
                'Secret': secret,
                'SecretDiscoveryDate': discovery_date})
        
        return _return if len(_return) > 1 else _return[0]
        

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
             'ZCMLConfiguration':
                [
                    {'package':'mellon.sniffers.test'},
                    {'package':'mellon.factories.test'},
                    {'package':'mellon.reporters.memory'},
                    {'package':'mellon_plugin.reporter.sqlalchemy.orm'}
                 ]
            }
        if config:
            _config.update(config)
        self.config = _config
        super(MellonOrmRuntimeReporterLayer, self).setUp()
        # We're gonna monkey-patch the default engine to make sure FK checks operate
        self.engine = self.create_engine()
        mellon_plugin.reporter.sqlalchemy.orm.db._Engine = self.engine
        mellon_plugin.reporter.sqlalchemy.orm.db._Commit = False # allow tearDown rollbacks
        self.session = get_session()
    
    def tearDown(self):
        reset_report()
        # expire the db engine/session globals.
        mellon_plugin.reporter.sqlalchemy.orm.db._session = False
        mellon_plugin.reporter.sqlalchemy.orm.db._Session = False
        mellon_plugin.reporter.sqlalchemy.orm.db._Engine = False
        super(MellonOrmRuntimeReporterLayer, self).tearDown()
MELLON_SA_ORM_REPORTER_RUNTIME_LAYER = MellonOrmRuntimeReporterLayer(mellon_plugin.reporter.sqlalchemy)

class MellonOrmExecutedReporterLayer(MellonOrmRuntimeReporterLayer):
    def setUp(self):
        super(MellonOrmExecutedReporterLayer, self).setUp()
        self.app.go()
        self.session.commit()
MELLON_SA_ORM_REPORTER_EXECUTED_LAYER = MellonOrmExecutedReporterLayer(mellon_plugin.reporter.sqlalchemy.orm)
