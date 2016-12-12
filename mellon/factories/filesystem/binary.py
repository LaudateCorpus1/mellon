import os
from binaryornot.check import is_binary
from zope import component
from zope import interface
import mellon

@interface.implementer(mellon.IBinaryChecker)
@component.adapter(mellon.IPath)
class BinaryCheckerForPath(object):
    
    def __init__(self, context):
        self.context = context
        self.path = str(context)
    
    def check(self):
        if os.path.isfile(self.path):
            if is_binary(self.path):
                return True
            try:
                with open(str(self.context)) as f:
                    i=50
                    while i:
                        f.readline()
                        i -= 1
                    pass
            except UnicodeDecodeError:
                return True
        return False