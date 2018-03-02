from zope import interface

class IPyramidConfigInitialized(interface.Interface):
    config = interface.Attribute("IPyramidConfig provider")

class IPyramidConfig(interface.Interface):
    """Marker for a Pyramid app configuration as returned by pyramid.config.Configurator()"""