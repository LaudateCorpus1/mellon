from zope import component
from zope import interface
from zope.component.factory import Factory
import mellon

from io import BytesIO
from io import StringIO

def get_default_mellon_test_files():
    """Return a list of IMellonFile providers suitable for testing purposes"""
    config = {
        'MellonSnippet':
            {
               'lines_coverage': 5,
               'lines_increment': 1,
               'bytes_read_size': 512000,
               'bytes_coverage': 8,
               'bytes_increment': 7
             }
        
        }
    config = component.createObject(u'sparc.config.container', config)
    
    files = []
    files.append(\
        component.createObject(u"mellon.unicode_file_from_stream", StringIO(
            u'test unicode file 1'), config)
    )
    files.append(\
        component.createObject(u"mellon.unicode_file_from_stream", StringIO(
            u'test unicode file 2'), config)
    )
    files.append(\
        component.createObject(u"mellon.byte_file_from_stream", BytesIO(
            b'test byte file 1'), config)
    )
    files.append(\
        component.createObject(u"mellon.byte_file_from_stream", BytesIO(
            b'test byte file 2'), config)
    )
    return files

@interface.implementer(mellon.IMellonFileProviderFactory, mellon.IMellonFileProvider)
class MellonFileProviderForTesting(object):
    """Class will deliver a series of IMellonFile providers.  To help keep
    testing simpler, MellonSnippet yaml config is already pre-defined.
    """
    def __init__(self, config):
        self.config = config #unused
        self.auth_context = component.createObject(\
                                    u"mellon.authorization_context", 
                                    identity='test_identity', 
                                    description='A mock auth context for testing')
        self.apply_context = component.getUtility(mellon.IApplyAuthorizationContext)
    
    def __iter__(self):
        for f in get_default_mellon_test_files():
            self.apply_context(self.auth_context, f)
            yield f

mellonFileProviderForTestingFactory = Factory(MellonFileProviderForTesting)