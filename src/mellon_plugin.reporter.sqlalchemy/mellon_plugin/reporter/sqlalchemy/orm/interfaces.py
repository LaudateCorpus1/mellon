from zope import interface

# BASES
# we separate the ORM data model vs the SA implementation-specific marker
class IORMModel(interface.Interface):
    """Base class for ORM models"""

class ISAModel(IORMModel):
    """Base class for all SQLAlchemy ORM models"""

# AUTHORIZATION CONTEXT
class IORMAuthorizationContext(IORMModel):
    id = interface.Attribute("Text unique identity")
    name = interface.Attribute("String representation of unique authorization context")
    description = interface.Attribute("Text context describer")
    
class ISAAuthorizationContext(ISAModel, IORMAuthorizationContext):
    """A SA ORM authorization context"""

# MELLON FILE
class IORMMellonFile(IORMModel):
    name = interface.Attribute("String locatable identity of file")
    authorization_context_id = interface.Attribute("Valid IORMAuthorizationContext.id reference")
    
class ISAMellonFile(ISAModel, IORMMellonFile):
    """A SA ORM mellon file"""

# SNIPPET
class IORMSnippet(IORMModel):
    id = interface.Attribute("String unique reference id for snippet")
    name = interface.Attribute("String internal snippet location information")
    data_blob = interface.Attribute("A Python byte data sequence")
    data_text = interface.Attribute("A Python unicode data sequence")
    mellon_file_name = interface.Attribute("Valid IORMMellonFile.name reference")
    
class ISASnippet(ISAModel, IORMSnippet):
    """A SA ORM snippet"""

# SECRET
class IORMSecret(IORMModel):
    id = interface.Attribute("String identifier that uniquely identifies the locatable secret among other secrets")
    name = interface.Attribute("String details of the secret and/or how it was found")
    snippet_id = interface.Attribute("valid IORMSnippet.id reference")
    
class ISASecret(ISAModel, IORMSecret):
    """A SA ORM secret"""

class IORMSecretDiscoveryDate(IORMModel):
    secret_id = interface.Attribute("valid IORMSecret.id reference")
    datetime = interface.Attribute("Python datetime")
    
class ISASecretDiscoveryDate(ISAModel, IORMSecretDiscoveryDate):
    """A SA ORM secret discovery date"""

class ISecretDiscoveryDates(interface.Interface):
    """Easy access to datetime information related to mellon.ISecret discoveries"""
    def all():
        """Iterator of ISASecretDiscoveryDate providers ordered from earliest"""
    def first():
        """Return oldest available ISASecretDiscoveryDate"""
    def last():
        """Return youngest available ISASecretDiscoveryDate"""