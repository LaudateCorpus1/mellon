from zope import interface

class IEveAuthProvider(interface.Interface):
    """Marker for an Eve auth provider that can be passed into runtime Eve app"""

class IEveSettings(interface.Interface):
    """Eve application configuration settings"""
    settings = interface.Attribute("Dict of valid Eve key value pairs")