import os.path
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin
from mellon.testing import MellonRuntimeLayerMixin
from mellon.reporters.memory import memory

base_path = os.path.dirname(__file__)

import mellon.sniffers.regex
class MellonSnifferRegExLayer(MellonRuntimeLayerMixin):
    pass
MELLON_REGEX_RUNTIME_LAYER = MellonSnifferRegExLayer(mellon.sniffers.regex)

class MellonSnifferRegExTestCase(unittest.TestCase):
    layer = MELLON_REGEX_RUNTIME_LAYER
    sm = component.getSiteManager()
    report = memory.report
    
    #expose the config so others might use it as well
    config = \
        {'MellonFileProviderFactory':
            {'name': 'mellon.factories.filesystem.file_provider_for_recursive_directory_config',
             'FileSystemDir':
                {'directory':os.path.join(base_path,'test_files')},
             'MellonSnippet':
                layer.config['MellonSnippet']
             },
         
         'MellonRegexSniffer':
            {'pattern_files':
                {'all': os.path.join(base_path,'test_regex_patterns_all.cfg'),
                 'byte':os.path.join(base_path,'test_regex_patterns_byte.cfg'),
                 'unicode':os.path.join(base_path,'test_regex_patterns_unicode.cfg')
                }
            }
        }
    
    def __init__(self, *args, **kwargs):
        self.layer.config.update(self.config)
        self.layer.config['ZCMLConfiguration'].append(
                                    {'package':'mellon.sniffers.regex'}
                                    )
        self.layer.config['ZCMLConfiguration'].append(
                                    {'package':'mellon.factories.filesystem'}
                                    )
        self.layer.verbose = False
        self.layer.debug = False
        super(MellonSnifferRegExTestCase, self).__init__(*args, **kwargs)
    
    def tearDown(self):
        memory.reset_report()
    
    def test_regex(self):
        # we'll perform a basic check...this could be dramatically improved :(
        self.assertEquals(memory.report, [])
        self.layer.run_app()
        self.assertEquals(len(memory.report), 4)
        
        

class test_suite(test_suite_mixin):
    layer = MELLON_REGEX_RUNTIME_LAYER
    package = 'mellon.sniffers.regex'
    module = 'regex'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(MellonSnifferRegExTestCase))
        return suite

if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])