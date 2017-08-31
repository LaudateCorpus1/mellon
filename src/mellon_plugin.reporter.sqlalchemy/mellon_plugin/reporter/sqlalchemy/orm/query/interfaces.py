from zope import interface
from zope.interface.common.sequence import IReadSequence
from zope import schema

from sqlalchemy import orm, sql


class IORMRelatedModels(interface.Interface):
    def flattened(seed):
        """Return non-circular sequence of IORMModel providers from seed starting point"""

class IORMRelatedModelsAdder(IORMRelatedModels):
    def add_sequence(sequence):
        """Add sequence of related IORMModel providers into graph"""

class ISAQuery(interface.Interface):
    """SQLAlchemy query object initialized with desired return items"""
interface.classImplements(orm.Query, ISAQuery)

class ISAOuterJoinQuery(ISAQuery):
    """SQLAlchemy query object initialized with outerjoin relationships between models"""

class ISAExpression(interface.Interface):
    """SQLAlchemy query filter expression that can be used within a conjunction"""

class ISAInstrumentedAttribute(interface.Interface):
    """SQLAlchemy ORM model attribute"""
interface.classImplements(orm.attributes.InstrumentedAttribute, ISAInstrumentedAttribute)

class ISAConjunction(interface.Interface):
    """Result from SQLAlchemy and_() or or_(), object represents conjunction of expressions"""
interface.classImplements(sql.expression.BooleanClauseList, ISAConjunction)

class ISAResultRowModel(interface.Interface):
    """SQLAlchemy model query result row parser"""
    def first(iface, row):
        """Return first result row model entry providing given interface
        
        Args:
            iface: zope.interface based specification
            row: sqlachemy query result row
        """

class ISAModelFilterExpression(interface.Interface):
    attribute = interface.Attribute(u"ISAModel attribute to filter by")
    condition = schema.Choice(
                title=u"Filter conditional matching logic",
                values=['==','equals','!=','not equals','like','ilike',
                        'in','not in','is null', 'is not null'],
                required=True
            )
    value = schema.Field(
                title=u"value to be used against filter condition",
                required=False
            )

class ISAModelFilterExpressionGroup(interface.Interface):
    conjunction = schema.Choice(
                title=u"Append logic for condition statements within the group",
                values=['AND','OR']
            )
    expressions = schema.Set(
                title=u"Group of expressions and sub-expression groups"
            )
