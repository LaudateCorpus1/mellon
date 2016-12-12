from zope.component.factory import Factory
from zope import interface
from . import ISecret

@interface.implementer(ISecret)
class Secret(object):
    def __init__(self, name, parent, hash_=None):
        self.__name__ = name
        self.__parent__ = parent
        self._hash = hash_ if hash_ else hash(name)
    def __str__(self):
        return self.__name__
    def __hash__(self):
        return self._hash
secretFactory = Factory(Secret)