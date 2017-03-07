from zope import interface
from zope import schema

class IORMRelatedModels(interface.Interface):
    def models(self):
        """Returns tuple of current sequence of models"""
    def initialize(models):
        """Re-initialize the models list with given sequence of IORMModel providers"""
    def inject(model, related=None):
        """Inject model into models list immediately after related.  If related
         is not given, then model is prepended to top of stack.  ValueError 
         raised if given related is not in models
        """

class ISAQuery(interface.Interface):
    """SQLAlchemy query object initialized with desired return items"""

class ISAOuterJoinQuery(ISAQuery):
    """SQLAlchemy query object initialized with outerjoin relationships between models"""

class ISAExpression(interface.Interface):
    """SQLAlchemy query filter expression that can be used within a conjunction"""

class ISAInstrumentedAttribute(interface.Interface):
    """SQLAlchemy ORM model attribute"""

class ISAConjunction(interface.Interface):
    """Result from SQLAlchemy and_() or or_(), object represents conjunction of expressions"""

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
