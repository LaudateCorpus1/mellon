from zope import interface

class IFlaskApplication(interface.Interface):
    """Marker for Thread local Flask application singleton"""

class IFlaskRequest(interface.Interface):
    """Marker for Thread local Flask request object"""

class IFlaskRestApiApplication(interface.Interface):
    """Marker for Flask Rest api singleton"""

class IFlaskRestApiResource(interface.Interface):
    """Marker for Flask Rest resource"""

class IFlaskRestApiPreprocessors(interface.Interface):
    """Marker for Flask Rest api preprocessor definition singleton"""

class IFlaskRestApiPostprocessors(interface.Interface):
    """Marker for Flask Rest api postprocessor definition singleton"""
