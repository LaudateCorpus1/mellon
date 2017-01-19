import hashlib
from zope.component.factory import Factory
from zope import interface
from . import ISecret

@interface.implementer(ISecret)
class Secret(object):
    def __init__(self, name, parent):
        self.__name__ = name
        self.__parent__ = parent
    def __str__(self):
        return self.__name__
    def get_id(self):
        """Based on Mellon file location string and secret string"""
        m = hashlib.md5()
        snippet = self.__parent__
        mfile = snippet.__parent__
        m.update("{}{}".format(self, mfile).encode('utf-8'))
        return m.hexdigest()
secretFactory = Factory(Secret)