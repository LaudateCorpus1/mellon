from mellon.testing import MellonApplicationRuntimeLayer
import mellon_plugin.reporter.sqlalchemy

class MellonOrmRuntimeWorkflowSeverityLayer(MellonApplicationRuntimeLayer):
    def setUp(self):
        self.config = \
            {
             'MellonWorkflowSecretAssignableSeverities':
                [
                    {'token': 'token_a',
                     'value': u'title a',
                     'description': u'description a'},
                    {'token': 'token_b',
                     'value': u'title b',
                     'description': u'description b'},
                 ],
             'ZCMLConfiguration':
                [
                    {'package':'mellon_plugin.reporter.sqlalchemy.orm.workflow'}
                ]
            }
        super(MellonOrmRuntimeWorkflowSeverityLayer, self).setUp()
MELLON_SA_ORM_WORKFLOW_SEVERITY_RUNTIME_LAYER = MellonOrmRuntimeWorkflowSeverityLayer(mellon_plugin.reporter.sqlalchemy)