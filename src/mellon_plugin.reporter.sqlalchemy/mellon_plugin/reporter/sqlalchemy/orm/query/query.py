from zope.component.factory import Factory
from zope import interface
from . import interfaces as qry_ifaces
from .. import models
from .. import db

from sparc.logging import logging
logger = logging.getLogger(__name__)

@interface.implementer(qry_ifaces.IORMRelatedModels)
class ORMRelatedModels(object):
    def __init__(self, models=None):
        self._models = [] if not models else [m for m in models]
    def models(self):
        return tuple(self._models)
    def initialize(self, models):
        self._models = [m for m in models]
    def inject(self, model, related=None):
        if not related:
            self._models.insert(0, model)
            return
        for i, m in enumerate(self._models):
            if m == related:
                self._models.insert(i+1, model)
                return
        raise ValueError("related not found in models")
ORMRelatedModelsFactory = Factory(ORMRelatedModels)

@interface.implementer(qry_ifaces.IORMRelatedModels)
class ORMRelatedModelsCore(ORMRelatedModels):
    def __init__(self):
        super(ORMRelatedModelsCore, self).__init__([models.MellonFile,
                                                    models.Snippet,
                                                    models.Secret
                                                    ])
ORMRelatedModelsCoreFactory = Factory(ORMRelatedModelsCore)

@interface.implementer(qry_ifaces.IORMRelatedModels)
class ORMRelatedModelsAuthContext(ORMRelatedModels):
    def __init__(self):
        super(ORMRelatedModelsAuthContext, self).__init__([
                         models.AuthorizationContext,
                         models.MellonFileAccessContext,
                         models.MellonFile,
                         models.Snippet,
                         models.Secret
                         ])
ORMRelatedModelsAuthContextFactory = Factory(ORMRelatedModelsAuthContext)

@interface.implementer(qry_ifaces.IORMRelatedModels)
class ORMRelatedModelsAll(ORMRelatedModels):
    def __init__(self):
        super(ORMRelatedModelsAll, self).__init__([
                         models.AuthorizationContext,
                         models.MellonFileAccessContext,
                         models.MellonFile,
                         models.Snippet,
                         models.Secret,
                         models.SecretDiscoveryDate
                         ])
ORMRelatedModelsAllFactory = Factory(ORMRelatedModelsAll)


@interface.implementer(qry_ifaces.ISAInstrumentedAttribute)
class SAInstrumentedAttributeFromDottedString(object):
    def __new__(self, dotted_name):
        class_name, property_name = dotted_name.split('.')
        base_classes = models.Base._decl_class_registry
        if class_name not in base_classes:
            raise TypeError('unable to find {} type in SQLAlchemy base classes {}'.format(class_name, base_classes.keys()))
        class_ = base_classes[class_name]
        property_ = getattr(class_, property_name)
        interface.alsoProvides(property_, qry_ifaces.ISAInstrumentedAttribute)
        return getattr(class_, property_name)
SAInstrumentedAttributeFromDottedStringFactory = Factory(SAInstrumentedAttributeFromDottedString)

@interface.implementer(qry_ifaces.ISAQuery)
class SAQuery(object):
    def __new__(cls, *args):
        q = db.get_session().query(*args)
        logger.debug("ISAQuery provider inited with args {}".format([a for a in args]))
        interface.alsoProvides(q, qry_ifaces.ISAQuery)
        return q
SAQueryFactory = Factory(SAQuery)
    

@interface.implementer(qry_ifaces.ISAOuterJoinQuery)
class SAOuterJoinQuery(object):
    def __new__(cls, left, models):
        """Return ISAOuterJoinQuery provider based on related models
        
        args:
            left: ISAModel considered as most left outer join
            models: sequence of ISAModel providers ordered left->right in terms
                    of required SQL query dependency structure.  
        """
        #re-order sequence based on selected left.  following this sample:
        # models = [1,2,3,4,5]
        # left = 4
        # ordered = [4,3,2,1,5]
        models = list(models)
        ordered = [left] + models[0:models.index(left)][::-1] + models[models.index(left)+1:]
        
        q = SAQuery(*ordered) # base query
        for m in ordered[1:]:
            q = q.outerjoin(m)
        interface.alsoProvides(q, qry_ifaces.ISAOuterJoinQuery)
        logger.debug("ISAOuterJoinQuery provider inited with left assignment {} and sequenced joins {}".format(left, ordered[1:]))
        return q
SAOuterJoinQueryFactory = Factory(SAOuterJoinQuery)

