from ..testing import MellonOrmRuntimeWorkflowLayer
import mellon_plugin.reporter.sqlalchemy

class MellonOrmRuntimeWorkflowSeverityLayer(MellonOrmRuntimeWorkflowLayer):
    def setUp(self, config=None):
        _config = \
            {
             'MellonWorkflowSecretAssignableSeverities':
                [
                    {'token': 'token_a',
                     'value': u'title a',
                     'description': u'description a'},
                    {'token': 'token_b',
                     'value': u'title b',
                     'description': u'description b'},
                 ]
            }
        if config:
            _config.update(config)
        super(MellonOrmRuntimeWorkflowSeverityLayer, self).setUp(_config)
MELLON_SA_ORM_WORKFLOW_SEVERITY_RUNTIME_LAYER = MellonOrmRuntimeWorkflowSeverityLayer(mellon_plugin.reporter.sqlalchemy)