from zope import interface

class IFlaskApplication(interface.Interface):
    """Marker for Flask application singleton"""

class IFlaskRestApiApplication(interface.Interface):
    """Marker for Flask Rest api singleton"""