from zope.component.factory import Factory
from zope import component
from zope import interface
from zope.schema.fieldproperty import FieldProperty
from sqlalchemy import and_, or_
from . import interfaces as qry_ifaces

@interface.implementer(qry_ifaces.ISAModelFilterExpression)
class SAModelFilterExpression(object):
    def __init__(self, *args, **kwargs):
        self.attribute = args[0] if len(args)>0 else kwargs['attribute']
        self.condition = args[1] if len(args)>1 else kwargs['condition']
        if len(args)>2 or 'value' in kwargs:
            self.value = args[2] if len(args)>2 else kwargs['value']
    condition = FieldProperty(qry_ifaces.ISAModelFilterExpression['condition'])
    value = FieldProperty(qry_ifaces.ISAModelFilterExpression['value'])
SAModelFilterExpressionFactory = Factory(SAModelFilterExpression)

@interface.implementer(qry_ifaces.ISAExpression)
@component.adapter(qry_ifaces.ISAModelFilterExpression)
class SAExpressionFromSAModelFilterExpression(object):
    def __new__(self, context):
        c = context.condition
        if c == '==' or c.lower() == 'equals':
            _return = context.attribute.__eq__(context.value)
        elif c == '!=' or c.lower() == 'not equals':
            _return = context.attribute.__ne__(context.value)
        elif c.lower() == 'like':
            _return = context.attribute.like(context.value)
        elif c.lower() == 'ilike':
            _return = context.attribute.ilike(context.value)
        elif c.lower() == 'in':
            _return = context.attribute.in_(context.value)
        elif c.lower() == 'not in':
            _return = ~context.attribute.in_(context.value)
        elif c.lower() == 'is null':
            _return = context.attribute.is_(None)
        elif c.lower() == 'is not null':
            _return = context.attribute.isnot(None)
        else:
            raise ValueError("received unexpected condition {}".format(c))
        interface.alsoProvides(_return, qry_ifaces.ISAExpression)
        return _return

@interface.implementer(qry_ifaces.ISAModelFilterExpressionGroup)
class SAModelFilterExpressionGroup(object):
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            self.conjunction = args[0]
        if 'conjunction' in kwargs:
            self.conjunction = kwargs['conjunction']
        if len(args) > 1:
            self.expressions = args[1]
        if 'expressions' in kwargs:
            self.expressions = kwargs['expressions']
    conjunction = FieldProperty(qry_ifaces.ISAModelFilterExpressionGroup['conjunction'])
    expressions = FieldProperty(qry_ifaces.ISAModelFilterExpressionGroup['expressions'])
SAModelFilterExpressionGroupFactory = Factory(SAModelFilterExpressionGroup)

def resolve_expression_group(eg):
    """Recursive expression group resolver
    
    Args:
        eg: ISAModelFilterExpressionGroup provider
    
    Returns:
        SQLAlchemy conjunction for given expression group
    """
    conj = and_ if eg.conjunction.upper() == 'AND' else or_
    expressions = []
    for cond in eg.expressions:
        if qry_ifaces.ISAModelFilterExpressionGroup.providedBy(cond):
            expressions.append(resolve_expression_group(cond))
        else: #ISAModelFilterExpression
            expressions.append(qry_ifaces.ISAExpression(cond))
    return conj(*expressions)

@interface.implementer(qry_ifaces.ISAConjunction)
@component.adapter(qry_ifaces.ISAModelFilterExpressionGroup)
class SAConjunctionFromSAModelFilterExpressionGroup(object):
    
    def __new__(cls, context):
        conj = resolve_expression_group(context)
        interface.alsoProvides(conj, qry_ifaces.ISAConjunction)
        return conj



def is_expression_container(container):
    return 'attribute' in container and 'condition' in container

def is_expression_group_container(container):
    return 'conjunction' in container and 'expressions' in container

def convert_expression_group_container(eg_container):
    """Recursive expression group container converter
    
    Args:
        eg_container: container with keys related to ISAModelFilterExpressionGroup containment
    
    Returns:
        ISAModelFilterExpressionGroup provider
    """
    conj = eg_container['conjunction'].upper()
    expressions = []
    for cond in eg_container['expressions']:
        if is_expression_group_container(cond):
            expressions.append(convert_expression_group_container(cond))
        else: #ISAModelFilterExpression container
            cond['attribute'] = component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.instrumented_attribute",
                    cond['attribute'])
            expressions.append(
                component.createObject(
                    u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression",
                    **cond))
    return component.createObject(
            u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group",
            conjunction=conj, expressions=set(expressions))

@interface.implementer(qry_ifaces.ISAModelFilterExpressionGroup)
class SAModelFilterExpressionGroupFromContainer(object):
    def __new__(self, container):
        """Return ISAModelFilterExpressionGroup based on formated container
        
        Container format should follow this paradigm:
            {
             'conjunction': 'and',
             'expressions':
                [
                 {'attribute':'model.field1', 'condition':'==', 'value':'value1'},
                 {'attribute':'model.field2', 'condition':'!=', 'value':'value2'},
                 {
                  'conjunction': 'or',
                  'expressions':
                      [
                       {'attribute':'model.field3', 'condition':'==', 'value':'value3'},
                       {'attribute':'model.field4', 'condition':'is null'}
                      ]
                 }
                ]
            }
        """
        return convert_expression_group_container(container)
SAModelFilterExpressionGroupFromContainerFactory = Factory(SAModelFilterExpressionGroupFromContainer)
