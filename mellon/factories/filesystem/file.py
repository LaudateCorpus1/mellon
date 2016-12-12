import collections
import os.path
from zope import component
from zope import interface
from zope.component.factory import Factory
from sparc.configuration import container
import mellon

@interface.implementer(mellon.IByteMellonFile)
class MellonByteFileFromFilePathAndConfig(object):
    
    def __init__(self, file_path, config):
        self.file_path = file_path
        self.config = config
        
    def __str__(self):
        return "byte file at location {}".format(self.file_path)

    def __iter__(self):
        with open(self.file_path, 'rb') as stream:
            file_ = component.createObject(u'mellon.byte_file_from_stream', stream, self.config)
            for snippet in file_:
                yield snippet
mellonByteFileFromFilePathAndConfigFactory = Factory(MellonByteFileFromFilePathAndConfig)

@interface.implementer(mellon.IUnicodeMellonFile)
class MellonUnicodeFileFromFilePathAndConfig(object):
    
    def __init__(self, file_path, config):
        self.file_path = file_path
        self.config = config
        
    def __str__(self):
        return "Unicode file at location {}".format(self.file_path)

    def __iter__(self):
        _end = 0
        _buffer = collections.deque()
        _eof_buffer = collections.deque()
        with open(str(self.file_path), 'rU') as stream:
            file_ = component.createObject(u'mellon.unicode_file_from_stream', stream, self.config)
            for snippet in file_:
                yield snippet
mellonUnicodeFileFromFilePathAndConfigFactory = Factory(MellonUnicodeFileFromFilePathAndConfig)

@interface.implementer(mellon.IMellonFileProvider)
class MellonFileProviderForRecursiveDirectoryConfig(object):
    
    def __init__(self, config):
        """Init
        
        Args:
            config: sparc.configuration.container.ISparcAppPyContainerConfiguration
                    provider with 
                    mellon.factories.filesystem[configure.yaml:FileSystemDir]
                    and mellon[configure.yaml:MellonSnippet] entries.
        """
        self.config = config
    
    def __iter__(self):
        base_path = container.IPyContainerConfigValue(self.config).\
                                            get('FileSystemDir')['directory']
        for d, dirs, files in os.walk(base_path):
            for f in files:
                path = os.path.join(d, f)
                if not os.path.isfile(path):
                    continue
                #get interface-assigned string (IPath)
                path = component.createObject(u'mellon.filesystem_path', path)
                if mellon.IBinaryChecker(path).check():
                    yield component.createObject(\
                        u'mellon.factories.filesystem.byte_file', path, self.config)
                else:
                    yield component.createObject(\
                        u'mellon.factories.filesystem.unicode_file', path, self.config)
    
mellonFileProviderForRecursiveDirectoryConfigFactory = Factory(MellonFileProviderForRecursiveDirectoryConfig)
interface.alsoProvides(mellonFileProviderForRecursiveDirectoryConfigFactory, mellon.IMellonFileProviderFactory)
