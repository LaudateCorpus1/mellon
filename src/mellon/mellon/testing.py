"""
We provide some sane starting points for Mellon test layers.  We have 3
starting layers:
 - A basic layer that loads the Mellon file based ZCML components
 - A Runtime layer that registers the Mellon application and configures it
 - An executed layer that runs the mellon application.
"""

from .mellon import create_and_register_app, get_registered_app
from .interfaces import IMellonApplication
from .reporters.memory.memory import reset_report
import mellon
from .interfaces import IPath, IBinaryChecker, IMellonApplication
from sparc.testing.testlayer import SparcZCMLFileLayer
from zope import component
from zope.component.testlayer import ZCMLLayerBase
from zope import interface

# A basic layer with Mellon ZCML components registered (does not include the
# mellon.IMellonApplication runtime component)
MELLON_INTEGRATION_LAYER = SparcZCMLFileLayer(mellon)

# A layer with a registered and configured, but unexecuted, Mellon application
"""
config_base = {'MellonSnippet':
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
"""
class MellonApplicationRuntimeLayer(ZCMLLayerBase):
    """
    Provides a configured and registered IMellonApplication layer (but 
    not executed).
    
    Most use-cases will want to extend this class, in doing so, have the 
    ability to update the runtime config.  Extenders can simply define their
    own class-level config property.
    
    A sample extension layer might look like this:
    import your.package
    class YourRuntimeLayer(MellonApplicationRuntimeLayer):
        
        def setUp(self):
            self.config = \
                {
                'ZCMLConfiguration': [{'package': 'your.plugin.package'},
                                      {'package': 'mellon.reporters.memory'},
                                      {'package': 'mellon', 'file': 'ftesting-bin_check-override.zcml'}
                                     ],
                'YourYamlEntry': 'some plugin yaml value'
                }
            super(YourRuntimeLayer, self).setUp() #should be called after config is defined
            
    YOUR_LAYER = YourRuntimeLayer(your.package)
    
    The above layer would make your plugin available along side a memory
    reporter (nice for easy testing purposes).  In addition, a file binary
    checker that only looks at file extensions is loaded (again, makes testing
    a little more sane).
    """
    verbose = False
    debug = False
    config = {}
    
    def setUp(self):
        super(MellonApplicationRuntimeLayer, self).setUp()
        self.app = create_and_register_app(self.config, self.verbose, self.debug)
        self.app.configure()

    def tearDown(self):
        reset_report() #added for convienence only...extenders would still need to register the memory reporter zcml
        """
        I don't think we need this because ZCMLLayerBase is our parent...it should
        be able to reset the component registry appropriately
        sm = component.getGlobalSiteManager()
        app = sm.getUtility(IMellonApplication)
        sm.unregisterUtility(component=app, provided=IMellonApplication)
        """
        super(MellonApplicationRuntimeLayer, self).tearDown()
    
    def _load_zcml(self, context):
        """Since the Mellon app does this for us, we need to pass
        """
        pass
        
MELLON_RUNTIME_LAYER = MellonApplicationRuntimeLayer(mellon)
    
# A layer with an executed Mellon application
class MellonApplicationExecutedLayer(MellonApplicationRuntimeLayer):
    """
    Provides environment for post-executed Mellon application.
    """
    def setUp(self):
        super(MellonApplicationExecutedLayer, self).setUp()
        component.getUtility(IMellonApplication).go()
        
MELLON_EXECUTED_LAYER = MellonApplicationExecutedLayer(mellon)

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