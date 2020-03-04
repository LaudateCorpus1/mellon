import argparse
import sys
from zope import component
from zope.dottedname.resolve import resolve
from zope import event
from zope import interface

from sparc.config import IConfigContainer
from sparc.config.container import SparcConfigContainer
from sparc.config.yaml.documents import SparcYamlConfigContainers
from sparc.component.configuration.config import handle_sparc_component_config_container
from sparc.logging import logging

from .events import SnippetAvailableForSecretsSniffEvent, MellonApplicationConfiguredEvent
from .interfaces import IMellonApplication, IMellonFileProvider, IWhitelistChecker
import mellon

def getScriptArgumentParser(description, args=sys.argv):
    """Return ArgumentParser object
    
    Args:
        description: Text description of application ArgumentParser will be
                     applied to.
    
    Kwargs:
        args (list):        list of arguments that will be parsed.  The default
                            is the sys.argv list, and should be correct for most
                            use cases.
    
    Returns:
        ArgumentParser object that can be used to validate and execute the
        current script invocation.
    """
    # Description
    parser = argparse.ArgumentParser(
            description=description)

    # config_file
    parser.add_argument('config_file',
            help="Valid script configuration file.  This should be the path to "\
                 "the script YAML configuration file.")
    
    # yaml parameters
    parser.add_argument('-r', '--parameters',
            help=\
            "Yaml template replacement context.  " +
            "This is a Python dotted name to an enumerable " +
            "mapping or a callable that returns an enumerable mapping." + 
            "Mapping values will replace matched keys in Yaml wrapped with " +
            "'mustaches' i.e.: {{SOME_KEY}}",
            default=None
            )
    
    # --verbose
    parser.add_argument('--verbose',
            action='store_true',
            help="Echo verbose messages to stdout.")
    
    # --debug
    parser.add_argument('--debug',
            action='store_true',
            help="Echo debug messages to stdout.")
    
    # --pdb
    parser.add_argument('--pdb', 
            help="drop to Python debugger for uncaught exceptions",
            action="store_true")
    
    return parser


DESCRIPTION="""\
Configurable secrets sniffer.  Application will examine runtime configuration
of Zope registry components and will search configured data against 
configured searches.  Matches will be logged via the Python logging
facility.
"""

@interface.implementer(IMellonApplication)
class Mellon(object):

    logger = logging.getLogger(__name__)
    
    def __init__(self, config=None, verbose=False, debug=False, pdb=False):
        """Init
        
        Args:
            config: ISparcAppPyContainerConfiguration compatible Py container for runtime configuration (i.e. a dict or list)
            verbose: True indicates verbose logging
            debug: True indicate debug logging
        """
        self.setLoggers(verbose, debug)
        self._pdb = pdb
        self._config = config 
    
    def get_config(self):
        return self._config
    
    def setLoggers(self, verbose, debug):
        logger = logging.getLogger() # root logger
        if verbose:
            logger.setLevel('INFO')
        if debug:
            logger.setLevel('DEBUG')

    def go(self):
        self.logger.info(u"searching for MellonFileProviderFactory entries in config file")
        for d in self.get_config().sequence('MellonFileProviderFactory'): #d is dict of MellonFileProviderFactories keys
            fprovider = component.createObject(d['name'], SparcConfigContainer(d)) #assumes named factory provides IMellonFileProviderFactory
            if not IMellonFileProvider.providedBy(fprovider):
                self.logger.warn(u"expected factory %s to create objects providing IMellonFileProvider, skipping" % str(d['name']))
                continue
            self.logger.info(u"found MellonFileProviderFactory config entry with name: {}".format(d['name']))
            try:
                for f in fprovider: # iterate the files in the provider
                    if component.getUtility(IWhitelistChecker).check(f):
                        self.logger.info(u"skipping white-listed file: {}".format(f))
                        continue
                    self.logger.info(u"searching for secrets in file: {} with authorization {}".format(f, mellon.IAuthorizationContext(f)))
                    for s in f: # iterate the data snippets in the file (s provides ISnippet)
                        #App reporters should subscribe to this event feed.  Each
                        #reporter is responsible to find/execute the sniffers and
                        #also to insure whitelisted secrets are not reported on.
                        event.notify(SnippetAvailableForSecretsSniffEvent(s))
            except Exception:
                import traceback, pdb
                if self._pdb:
                    type, value, tb = sys.exc_info()
                    traceback.print_exc()
                    pdb.post_mortem(tb)
                else:
                    traceback.print_exc()
        self.logger.info(u"completed MellonFileProviderFactory config file entry search")


def get_contour_config_container(yaml_configuration_file=None,
                                 yaml_parameters=None):
    """Return a sparc.config.IConfigContainer provider
    
    If yaml_configuration_file is not provided, then a container is returned
    with default entries
    
    Kwargs:
        yaml_configuration_file: String file path to valid Contour App Yaml
            configuration file.
    
    Returns:
        :class:`sparc.config.interfaces.IConfigContainer` provider for current 
        Contour app runtime
    """
    if yaml_configuration_file:
        c_container = SparcYamlConfigContainers().\
                        first(yaml_configuration_file, 
                            get_yaml_parameters(yaml_parameters))
    else:
        c_container = SparcConfigContainer({'ZopeComponentConfiguration':
                                                {'zcml':
                                                    [{'package': 'mellon'}]
                                                }
                                            })
    return c_container
    
def get_yaml_parameters(yaml_parameters):
    """Returns enumerable mapping
    
    Args:
        yaml_parameters:  either a mapping or a callable that returns a mapping
    """
    if hasattr(yaml_parameters, '__call__'):
        v = yaml_parameters()
        if hasattr(v, '__getitem__'):
            return v
    if not hasattr(yaml_parameters, '__getitem__'):
        return {}
    return yaml_parameters
    
def create_app(config, verbose=False, debug=False):
    if not IConfigContainer.providedBy(config):
        config = SparcConfigContainer(config)
    handle_sparc_component_config_container(config) #registers components
    app = Mellon(config=config, verbose=verbose,debug=debug)
    app.verbose = verbose
    app.debug = debug
    return app
    
def register_app(app):
    sm = component.getSiteManager()
    sm.registerUtility(app, IMellonApplication) #give components access to app config

def create_and_register_app(config, verbose=False, debug=False):
    app = create_app(config, verbose, debug)
    register_app(app)
    event.notify(MellonApplicationConfiguredEvent(app))
    return app

def get_registered_app():
    """Return a dict with app, config, and config value getter for currently 
    registered mellon.IMellonApplication utility
    
    Return:
        {'app':     mellon.IMellonApplication provider
         'config':  sparc.config.IConfigContainer provider
         'vgetter': sparc.config.IHierarchyMapping provider
        }
    """
    app = component.getUtility(IMellonApplication)
    config = app.get_config()
    return {'app':app,'config':config,'vgetter':config.mapping()}

def main():
    args = getScriptArgumentParser(DESCRIPTION).parse_args()
    c_container = get_contour_config_container(args.config_file, 
                            resolve(args.parameters) if args.parameters else None)
    create_and_register_app(c_container, args.verbose, args.debug)
    app = component.getUtility(IMellonApplication) #test registration and go
    app.go() 

if __name__ == '__main__':
    main()
