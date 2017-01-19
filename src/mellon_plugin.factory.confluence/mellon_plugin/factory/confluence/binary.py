from zope import interface
from zope.component.factory import Factory
import mellon

@interface.implementer(mellon.IBinaryChecker)
class BinaryCheckerForConfluenceItem(object):
    
    def __init__(self, item):
        self.item = item
    
    def check(self):
        if 'attachment' == self.item.get('type', False):
            return True
        return False
binaryCheckerForConfluenceItemFactory = Factory(BinaryCheckerForConfluenceItem)