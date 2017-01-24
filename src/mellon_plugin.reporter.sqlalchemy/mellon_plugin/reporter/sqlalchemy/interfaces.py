from zope import interface

class IDBReporter(interface.Interface):
    
    def initialized():
        """Returns True if database schema is installed"""
    
    def update_schema():
        """Updates the database schema if needed"""
    
    def report(secret):
        """Report a new secret
        
        Args:
            secret: mellon.ISecret provider to be reported
        """