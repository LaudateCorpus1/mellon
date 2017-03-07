from zope import interface
from zope.component.factory import Factory
from mellon_plugin.reporter.sqlalchemy.orm import models as mellon_models
from mellon_plugin.reporter.sqlalchemy.orm.query import interfaces as qry_ifaces
from mellon_plugin.reporter.sqlalchemy.orm.query.query import ORMRelatedModels
from .. import models as workflow_models


@interface.implementer(qry_ifaces.IORMRelatedModels)
class ORMRelatedModelsWorkflowCore(ORMRelatedModels):
    def __init__(self):
        super(ORMRelatedModelsWorkflowCore, self).__init__(
                        [mellon_models.MellonFile,
                         mellon_models.Snippet,
                         mellon_models.Secret,
                         workflow_models.SecretSeverity,
                         workflow_models.SecretStatus
                        ])
ORMRelatedModelsWorkflowCoreFactory = Factory(ORMRelatedModelsWorkflowCore)

@interface.implementer(qry_ifaces.IORMRelatedModels)
class ORMRelatedModelsWorkflowAuthorizationContext(ORMRelatedModels):
    def __init__(self):
        super(ORMRelatedModelsWorkflowAuthorizationContext, self).__init__(
                        [mellon_models.AuthorizationContext,
                         mellon_models.MellonFileAccessContext,
                         mellon_models.MellonFile,
                         mellon_models.Snippet,
                         mellon_models.Secret,
                         workflow_models.SecretSeverity,
                         workflow_models.SecretStatus
                        ])
ORMRelatedModelsWorkflowAuthorizationContextFactory = Factory(ORMRelatedModelsWorkflowAuthorizationContext)

@interface.implementer(qry_ifaces.IORMRelatedModels)
class ORMRelatedModelsWorkflowAll(ORMRelatedModels):
    def __init__(self):
        super(ORMRelatedModelsWorkflowAll, self).__init__(
                        [mellon_models.AuthorizationContext,
                         mellon_models.MellonFileAccessContext,
                         mellon_models.MellonFile,
                         mellon_models.Snippet,
                         mellon_models.Secret,
                         workflow_models.SecretSeverity,
                         workflow_models.SecretStatus,
                         mellon_models.SecretDiscoveryDate
                        ])
ORMRelatedModelsWorkflowAllFactory = Factory(ORMRelatedModelsWorkflowAll)


