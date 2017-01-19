from zope.component.factory import Factory
from zope import interface
from . import IPath

@interface.implementer(IPath)
class FilesystemPath(str):
    pass
filesystemPathFactory = Factory(FilesystemPath)