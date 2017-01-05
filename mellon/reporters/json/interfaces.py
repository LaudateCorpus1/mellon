from zope import interface

# copied directly from zope.container.interfaces
class ISecretJsonTransformer(interface.Interface):
    def transform(secret):
        """Return a JSON string representing a secret
        
        JSON structure is an implementation detail
        
        Args:
            secret: mellon.ISecret provider
        
        Return:
            JSON String
        """
