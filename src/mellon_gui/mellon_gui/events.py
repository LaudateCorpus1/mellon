from zope import interface
from .interfaces import IPyramidConfigInitialized

@interface.implementer(IPyramidConfigInitialized)
class PyramidConfigInitialized(object):
    def __init__(self, config):
        self.config = config