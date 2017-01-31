from ..testing import MellonOrmRuntimeWorkflowLayer
import mellon_plugin.reporter.sqlalchemy

class MellonOrmRuntimeWorkflowStatusLayer(MellonOrmRuntimeWorkflowLayer):
    def setUp(self, config=None):
        _config = \
            {
             'MellonWorkflowSecretAssignableStatuses':
                [
                    {'token': 'token_1',
                     'value': u'title 1',
                     'description': u'description 1'},
                    {'token': 'token_2',
                     'value': u'title 2',
                     'description': u'description 2'},
                 ]
            }
        if config:
            _config.update(config)
        super(MellonOrmRuntimeWorkflowStatusLayer, self).setUp(_config)
MELLON_SA_ORM_WORKFLOW_STATUS_RUNTIME_LAYER = MellonOrmRuntimeWorkflowStatusLayer(mellon_plugin.reporter.sqlalchemy)