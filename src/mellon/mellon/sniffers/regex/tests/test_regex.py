import os.path
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from mellon import testing
from mellon.reporters.memory import memory

base_path = os.path.dirname(__file__)

import mellon.sniffers.regex
class MellonSnifferRegExExecutedLayer(testing.MellonApplicationExecutedLayer):
    
    
    def setUp(self):
        self.config = \
            {'MellonFileProviderFactory':
                {'name': 'mellon.factories.filesystem.file_provider_for_recursive_directory_config',
                 'FileSystemDir':
                    {'directory':os.path.join(base_path,'test_files')},
                 'MellonSnippet':
                    {'lines_coverage': 2,
                     'lines_increment': 1,
                     'bytes_read_size': 8,
                     'bytes_coverage': 4,
                     'bytes_increment': 3
                     }
                 },
             
             'MellonRegexSniffer':
                {'pattern_files':
                    {'all': os.path.join(base_path,'test_regex_patterns_all.cfg'),
                     'byte':os.path.join(base_path,'test_regex_patterns_byte.cfg'),
                     'unicode':os.path.join(base_path,'test_regex_patterns_unicode.cfg')
                    }
                },
             'ZCMLConfiguration':
                [{'package':'mellon.sniffers.regex'},
                 {'package':'mellon.reporters.memory'},
                 {'package':'mellon.factories.filesystem'}]
            }
        super(MellonSnifferRegExExecutedLayer, self).setUp()
        
MELLON_SNIFFER_REGEX_EXECUTED_LAYER = MellonSnifferRegExExecutedLayer(mellon.sniffers.regex)

class MellonSnifferRegExTestCase(unittest.TestCase):
    layer = MELLON_SNIFFER_REGEX_EXECUTED_LAYER
    
    def test_regex(self):
        # we'll perform a basic check...this could be dramatically improved :(
        self.assertEqual(len(memory.report), 4)

class test_suite(test_suite_mixin):
    layer = MELLON_SNIFFER_REGEX_EXECUTED_LAYER
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