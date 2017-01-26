from datetime import datetime
import sqlalchemy
from sqlalchemy.engine import reflection
from zope import component
from zope import interface
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

@interface.implementer(IDBReporter)
class DBReporter(object):

    def __init__(self):
        m = mellon.mellon.get_registered_app()
        _dsn = m['vgetter'].get('SQLAlchemyLoggerReporter','SQLAlchemyReporter','SQLAlchemyEngine','dsn')
        _kwargs = m['vgetter'].get('SQLAlchemyLoggerReporter','SQLAlchemyReporter','SQLAlchemyEngine','kwargs', default={})
        if m['app'].debug:
            _kwargs['echo'] = True
        self.engine = sqlalchemy.create_engine(_dsn, **_kwargs)
        self.table_name = m['vgetter'].get('SQLAlchemyLoggerReporter','SQLAlchemyReporter','SQLAlchemyEngine','table_name', default='secrets')
        self.utc_time = m['vgetter'].get('SQLAlchemyLoggerReporter','SQLAlchemyReporter','SQLAlchemyEngine','utc_time', default=False)

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
    
    def report(self, secret):
        snippet = secret.__parent__
        mfile = snippet.__parent__
        connection = self.engine.connect()
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