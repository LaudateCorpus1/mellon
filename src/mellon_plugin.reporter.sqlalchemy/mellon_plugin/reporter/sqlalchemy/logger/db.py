from datetime import datetime
import sqlalchemy
from sqlalchemy.engine import reflection
from zope import component
from zope import interface
import mellon
from sparc.configuration import container
from .interfaces import IDBReporter

from sparc.logging import logging
import mellon_plugin
logger = logging.getLogger(__name__)

reporter = None #module-level holder for initialized IDBReporter singleton

@component.adapter(mellon.ISecretDiscoveredEvent)
def db_reporter_for_secret(event):
    secret = event.object
    snippet = secret.__parent__
    mfile = snippet.__parent__
    if not reporter:
        mellon_plugin.reporter.sqlalchemy.logger.db.reporter = component.getUtility(IDBReporter)
        if not reporter.initialized():
            reporter.update_schema()
    reporter.report(secret)
    logging.debug(\
                u"Found secret in file snippet.  Secret information: [{}]. Secret unique identifier [{}]. Snippet information: [{}].  File information: [{}].  Authorization context information [{}]"\
                .format(secret, secret.get_id(), snippet.__name__, mfile, mellon.IAuthorizationContext(snippet)))

@interface.implementer(IDBReporter)
class DBReporter(object):

    def __init__(self):
        app = component.getUtility(mellon.IMellonApplication)
        config_app = app.get_config()
        config_reporter = container.IPyContainerConfigValue(config_app).get('SQLAlchemyReporter')
        _dsn = config_reporter['SQLAlchemyEngine']['dsn']
        _kwargs = config_reporter['SQLAlchemyEngine'].get('kwargs', {})
        if app.debug:
            _kwargs['echo'] = True
        self.engine = sqlalchemy.create_engine(_dsn, **_kwargs)
        self.table_name = config_reporter['SQLAlchemyEngine'].get('table_name', 'secrets')
        self.utc_time = config_reporter['SQLAlchemyEngine'].get('utc_time', False)
        
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