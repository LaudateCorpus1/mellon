from zope import interface

class IEveApplicationKwargs(interface.Interface):
    """Marker for kwargs singleton to be delivered into IEveApplication singleton"""
    kwargs = interface.Attribute("Dict of kwargs to be given to IEveApplication singleton")
