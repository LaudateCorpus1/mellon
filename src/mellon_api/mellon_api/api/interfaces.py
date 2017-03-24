from zope import interface
from zope import schema as zschema

class IAPISAEndpoint(interface.Interface):
    """An API endpoint with SQLAlchemy backend storage"""
    model = zschema.Field(
                title=u"ISAModel provider",
                required=True,
                readonly=True
            )
    resource = zschema.Field(
                title=u"mellon_api.IFlaskRestApiResource provider",
                required=True,
                readonly=True
            )
    schema = zschema.Field(
                title=u"IMMSchema provider",
                required=True,
                readonly=True
            )
    routes = zschema.Iterable(
                title=u"Iterable of string Flask url routes",
                required=True,
                readonly=True
            )
    endpoint = zschema.ASCIILine(
                title=u"String endpoint identity (used for internal mapping)",
                required=True,
                readonly=True
            )

class IAPISAEndpoints(interface.Interface):
    """API enpoints collection"""
    map = zschema.Dict(
                title=u"keys are IAPISAEndpoint.endpoint, values are related IAPISAEndpoint",
                required=True
            )

class IAPISAEndpointLookup(interface.Interface):
    """Endpoint lookup"""
    def lookup(entry):
        """Return IAPIEndpoint provider related to entry
        
        entry is one of:
            - IAPISAEndpoint.resource.Meta.type_
        
        Raises LookupError if entry could not be found
        """

class IMMSchema(interface.Interface):
    """Marker for a Marshmallow schema"""

class IMMSchemaMeta(interface.Interface):
    """Marker for a Marshmallow schema Meta"""


class IAPIRequestResourceInclude(interface.Interface):
    include = zschema.TextLine(
                title=u"URI encoded resource filter JSON string",
                description=u"see http://jsonapi.org/format/#fetching-includes",
                required=True,
                readonly=True
            )


class IAPIWorkflowAssignmentInfo(interface.Interface):
    """Defined workflow information used for assignment"""
    token = zschema.ASCIILine(
                title=u"Token identity",
                description=u"A Token that represents the workflow attribute",
                required=True,
                readonly=True
            )
    value = zschema.TextLine(
                title=u"Value for display",
                description=u"A value for display",
                required=True,
                readonly=True
            )
    description = zschema.Text(
                title=u"Description for display",
                description=u"A description for display",
                required=True,
                readonly=True
            )

class IAPIWorkflowStatus(IAPIWorkflowAssignmentInfo):
    """Defined workflow status information"""

class IAPIWorkflowSeverity(IAPIWorkflowAssignmentInfo):
    """Defined workflow severity information"""