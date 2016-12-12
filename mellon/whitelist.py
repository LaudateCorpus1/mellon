from zope.component.factory import Factory
from zope import interface
from .interfaces import IWhitelistInfo

@interface.implementer(IWhitelistInfo)
class WhitelistInfo(str):
    pass
whitelistInfoFactory = Factory(WhitelistInfo)