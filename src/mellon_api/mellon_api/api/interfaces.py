from zope import interface
from zope import schema

class IAPIWorkflowAssignmentInfo(interface.Interface):
    """Defined workflow information used for assignment"""
    token = schema.ASCIILine(
                title=u"Token identity",
                description=u"A Token that represents the workflow attribute",
                required=True,
                readonly=True
            )
    value = schema.TextLine(
                title=u"Value for display",
                description=u"A value for display",
                required=True,
                readonly=True
            )
    description = schema.Text(
                title=u"Description for display",
                description=u"A description for display",
                required=True,
                readonly=True
            )

class IAPIWorkflowStatus(IAPIWorkflowAssignmentInfo):
    """Defined workflow status information"""

class IAPIWorkflowSeverity(IAPIWorkflowAssignmentInfo):
    """Defined workflow severity information"""