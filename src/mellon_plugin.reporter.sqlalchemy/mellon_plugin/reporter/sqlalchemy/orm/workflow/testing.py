from ..testing import MellonOrmRuntimeReporterLayer
import mellon_plugin.reporter.sqlalchemy

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
MELLON_SA_ORM_WORKFLOW_RUNTIME_LAYER = MellonOrmRuntimeWorkflowLayer(mellon_plugin.reporter.sqlalchemy)