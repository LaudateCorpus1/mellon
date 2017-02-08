from zope import interface

class ISAEngine(interface.Interface):
    """Marker for a SA Engine object"""

class ISASession(interface.Interface):
    """Marker for a Session factory object that creates usable sessions"""