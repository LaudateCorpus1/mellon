from ..testing import MellonOrmRuntimeReporterLayer
import mellon_plugin.reporter.sqlalchemy
from .. import models as orm_models
from . import models as workflow_models

class MellonOrmRuntimeWorkflowLayer(MellonOrmRuntimeReporterLayer):
    def setUp(self, config=None):
        _config = \
            {
             'ZCMLConfiguration':
                [
                    {'package':'mellon_plugin.reporter.sqlalchemy.orm.workflow'}
                ]
            }
        if config:
            _config.update(config)
        super(MellonOrmRuntimeWorkflowLayer, self).setUp(_config)
    
    def create_full_model(self, count=1):
        r = MellonOrmRuntimeReporterLayer.create_full_model(self, count=count)
        return r
    
    def create_complex_model(self):
        MellonOrmRuntimeReporterLayer.create_complex_model(self)
        self.add_workflow_to_all_secrets()
    
    def add_workflow_to_all_secrets(self):
        severity_token = 'default_severity'
        status_token = 'default_status'
        for secret in self.session.query(orm_models.Secret).all():
            self.session.add(workflow_models.SecretSeverity(
                                token=severity_token, secret_id = secret.id))
            self.session.add(workflow_models.SecretStatus(
                                token=status_token, secret_id = secret.id))
        self.session.flush()
        
MELLON_SA_ORM_WORKFLOW_RUNTIME_LAYER = MellonOrmRuntimeWorkflowLayer(mellon_plugin.reporter.sqlalchemy)