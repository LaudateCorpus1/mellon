from .mellon import create_and_register_app
import mellon
from .interfaces import IPath, IBinaryChecker
from sparc.testing.testlayer import SparcZCMLFileLayer
from zope import component
from zope.component.testlayer import LayerBase
from zope import interface
import shutil
import tempfile

MELLON_INTEGRATION_LAYER = SparcZCMLFileLayer(mellon)


class MellonRuntimeLayerMixin(LayerBase):
    """
    Provides base components to enable installation of a Mellon runtime
    environment.
    """
    
    config = {'MellonSnippet':
                {'lines_coverage': 2,
                 'lines_increment': 1,
                 'bytes_read_size': 8,
                 'bytes_coverage': 4,
                 'bytes_increment': 3
                 },
              'ZCMLConfiguration':
                [{'package': 'mellon.reporters.memory'},
                 {'package': 'mellon',
                  'file': 'ftesting-bin_check-override.zcml'}
                 ]
              }
    verbose = False
    debug = False
    
    def run_app(self):
        app = create_and_register_app(self.config, self.verbose, self.debug)
        app.configure()
        app.go()
    
    def setUp(self):
        super(MellonRuntimeLayerMixin, self).setUp()
        self.working_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        if len(self.working_dir) < 3:
            print('ERROR: working directory less than 3 chars long, unable to clean up: %s' % str(self.working_dir))
            return
        shutil.rmtree(self.working_dir)
        super(MellonRuntimeLayerMixin, self).tearDown()

"""
A Sample runtime app test case...

import your.package
from mellon.testing import MellonRuntimeLayerMixin
class MellonRuntimeLayerExample(MellonRuntimeLayerMixin):
    # Allow registry setup/teardown at test case level
    pass
EXAMPLE_RUNTIME_LAYER = MellonRuntimeLayerExample(your.package)

import unittest
from mellon.reporters.memory import memory
class MellonRuntimeTestExample(unittest.TestCase):
    layer = EXAMPLE_RUNTIME_LAYER
    report = memory.report
    
    def tearDown(self):
        memory.reset_report()

    def test_example(self):
        self.layer.config = {'ExampleConfigEntry': None}
        self.layer.run_app()
        self.assertEquals(self.report[0], 'Some ISecret string')
"""
        
@interface.implementer(IBinaryChecker)
@component.adapter(IPath)
class RegexTesterBinaryChecker(object):
    def __init__(self, context):
        self.context = context
    
    def check(self):
        return True if self.context[-3:] == 'bin' else False