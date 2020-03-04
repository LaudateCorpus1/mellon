from datetime import datetime
from zope import component
from zope import interface
import sqlalchemy
from sqlalchemy.engine import reflection
import mellon
from .interfaces import IDBReporter

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(mellon.ISecretDiscoveredEvent)
def db_reporter_for_secret(event):
    secret = event.object
    snippet = secret.__parent__
    mfile = snippet.__parent__
    reporter = component.getUtility(IDBReporter)
    reporter.report(secret)
    logger.debug(\
                u"Found secret in file snippet.  Secret information: [{}]. Secret unique identifier [{}]. Snippet information: [{}].  File information: [{}].  Authorization context information [{}]"\
                .format(secret, secret.get_id(), snippet.__name__, mfile, mellon.IAuthorizationContext(snippet)))


@component.adapter(mellon.IMellonApplication, mellon.IMellonApplicationConfiguredEvent)
def initialize_db(app, event):
    db_init = DbInitializer()
    DBReporter.initializer = db_init
    DBReporter.tables = db_init.tables
    DBReporter.utc_time = db_init.utc_time

class DbInitializer(object):

    def __init__(self):
        m = mellon.mellon.get_registered_app()
        _dsn = m['vgetter'].get_value('SQLAlchemyLoggerReporter','SQLAlchemyReporter','SQLAlchemyEngine','dsn')
        _kwargs = m['vgetter'].get_value('SQLAlchemyLoggerReporter','SQLAlchemyReporter','SQLAlchemyEngine','kwargs', default={})
        if m['app'].debug:
            _kwargs['echo'] = True
        self.engine = sqlalchemy.create_engine(_dsn, **_kwargs)
        self.table_name = m['vgetter'].get_value('SQLAlchemyLoggerReporter','SQLAlchemyReporter','SQLAlchemyEngine','table_name', default='secrets')
        self.utc_time = m['vgetter'].get_value('SQLAlchemyLoggerReporter','SQLAlchemyReporter','SQLAlchemyEngine','utc_time', default=False)

        self.metadata = sqlalchemy.MetaData()
        self.tables = {
              'secrets': 
                    sqlalchemy.Table(self.table_name, self.metadata,
                        sqlalchemy.Column('entry_id', sqlalchemy.Integer,
                                      primary_key=True, autoincrement=True),
                        sqlalchemy.Column('entry_datetime', sqlalchemy.DateTime, nullable=False),
                        sqlalchemy.Column('secret_id', sqlalchemy.String, nullable=False),
                        sqlalchemy.Column('secret_info', sqlalchemy.Text, nullable=False),
                        sqlalchemy.Column('snippet_info', sqlalchemy.Text, nullable=False),
                        sqlalchemy.Column('file_info', sqlalchemy.Text, nullable=False),
                        sqlalchemy.Column('auth_context_info', sqlalchemy.Text, nullable=False)
                    )
              }
        
        if not self.initialized():
            logger.debug(u"Initializing sqlalchemy schema for logging")
            self.update_schema()

    
    def update_schema(self):
        self.metadata.create_all(self.engine)
    
    def initialized(self):
        insp = reflection.Inspector.from_engine(self.engine)
        return self.table_name in insp.get_table_names()

@interface.implementer(IDBReporter)
class DBReporter(object):
    
    initializer = None #initialized by .subscribers.initialize_db
    tables = None #initialized by .subscribers.initialize_db
    utc_time = None #initialized by .subscribers.initialize_db
    
    def report(self, secret):
        snippet = secret.__parent__
        mfile = snippet.__parent__
        connection = self.initializer.engine.connect()
        ins = self.tables['secrets'].insert().values(
                    entry_datetime=datetime.now() if not self.utc_time else datetime.utcnow(),
                    secret_id = secret.get_id(),
                    secret_info = str(secret),
                    snippet_info = snippet.__name__,
                    file_info = str(mfile),
                    auth_context_info = str(mellon.IAuthorizationContext(snippet))
                )
        result = connection.execute(ins)
        result.close()
        connection.close()