from zope import component
from zope.component.factory import Factory
from zope import interface
from .interfaces import IWhitelist, IWhitelistInfo, IWhitelistChecker

from sparc.logging import logging
logger = logging.getLogger(__name__)

@interface.implementer(IWhitelistInfo)
class WhitelistInfo(str):
    pass
whitelistInfoFactory = Factory(WhitelistInfo)


@interface.implementer(IWhitelistChecker)
class WhitelistChecker(object):
    
    def __init__(self):
        self.sm = component.getSiteManager()
    
    def check(self, item):
        wht_lstd = False
        for wht_lst in component.subscribers((item,), IWhitelist):
            for wht_lst_info in wht_lst:
                self.logger.debug(u"found white-list entry {} for item: {}".format(wht_lst_info, item))
                wht_lstd = True
        return True if wht_lstd else False