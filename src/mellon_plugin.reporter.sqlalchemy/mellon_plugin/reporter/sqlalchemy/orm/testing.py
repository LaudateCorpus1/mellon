from mellon.testing import MellonApplicationRuntimeLayer
from mellon.reporters.memory.memory import reset_report
from sqlalchemy import create_engine, event
import mellon_plugin.reporter.sqlalchemy.orm
from .db import get_session

class MellonOrmRuntimeReporterLayer(MellonApplicationRuntimeLayer):
    
    def create_engine(self):
        #http://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
        def _fk_pragma_on_connect(dbapi_con, con_record):
            dbapi_con.execute('pragma foreign_keys=ON')
        engine = create_engine('sqlite:///:memory:', echo=self.debug)
        event.listen(engine, 'connect', _fk_pragma_on_connect)
        return engine
    

    def setUp(self):
        self.config = \
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
        super(MellonOrmRuntimeReporterLayer, self).setUp()
        # We're gonna monkey-patch the default engine to make sure FK checks operate
        self.engine = self.create_engine()
        mellon_plugin.reporter.sqlalchemy.orm.db._Engine = self.engine
        self.session = get_session()
    
    def tearDown(self):
        reset_report()
        super(MellonOrmRuntimeReporterLayer, self).tearDown()
MELLON_SA_ORM_REPORTER_RUNTIME_LAYER = MellonOrmRuntimeReporterLayer(mellon_plugin.reporter.sqlalchemy)

class MellonOrmExecutedReporterLayer(MellonOrmRuntimeReporterLayer):
    def setUp(self):
        super(MellonOrmExecutedReporterLayer, self).setUp()
        self.app.go()
MELLON_SA_ORM_REPORTER_EXECUTED_LAYER = MellonOrmExecutedReporterLayer(mellon_plugin.reporter.sqlalchemy.orm)
