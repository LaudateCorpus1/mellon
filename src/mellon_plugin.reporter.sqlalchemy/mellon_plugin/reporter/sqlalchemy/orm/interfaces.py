from zope import interface

class IORMModel(interface.Interface):
    """Base class for ORM models"""

class IORMAuthorizationContext(IORMModel):
    id = interface.Attribute("Text unique identity")
    name = interface.Attribute("String representation of unique authorization context")
    description = interface.Attribute("Text context describer")

class IORMMellonFile(IORMModel):
    name = interface.Attribute("String locatable identity of file")
    authorization_context_id = interface.Attribute("Valid IORMAuthorizationContext.id reference")

class IORMSnippet(IORMModel):
    id = interface.Attribute("String unique reference id for snippet")
    name = interface.Attribute("String internal snippet location information")
    data_blob = interface.Attribute("A Python byte data sequence")
    data_text = interface.Attribute("A Python unicode data sequence")
    mellon_file_name = interface.Attribute("Valid IORMMellonFile.name reference")

class IORMSecret(IORMModel):
    id = interface.Attribute("String identifier that uniquely identifies the locatable secret among other secrets")
    name = interface.Attribute("String details of the secret and/or how it was found")
    snippet_id = interface.Attribute("valid IORMSnippet.id reference")