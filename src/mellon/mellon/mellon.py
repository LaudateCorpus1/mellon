import traceback
from zope import component
from zope import event
from zope import interface

from sparc.configuration import container
from sparc.configuration.container import application
from sparc.configuration import yaml
from sparc.logging import logging

from .events import SnippetAvailableForSecretsSniffEvent
import mellon

DESCRIPTION="""\
Configurable secrets sniffer.  Application will examine runtime configuration
of Zope registry components and will search configured data against 
configured searches.  Matches will be logged via the Python logging
facility.
"""

@interface.implementer(mellon.IMellonApplication)
class Mellon(application.YamlCliAppMixin):

    logger = logging.getLogger(__name__)
    app_zcml = (mellon, 'configure.zcml')

    def go(self):
        v_iter = component.getUtility(container.ISparcPyDictValueIterator)
        self.logger.info(u"searching for MellonFileProviderFactory entries in config file")
        for d in v_iter.values(self.get_config(), 'MellonFileProviderFactory'): #d is dict of MellonFileProviderFactories keys
            fprovider = component.createObject(d['name'], d) #assumes named factory provides IMellonFileProviderFactory
            if not mellon.IMellonFileProvider.providedBy(fprovider):
                self.logger.warn(u"expected factory %s to create objects providing IMellonFileProvider, skipping" % str(d['name']))
                continue
            self.logger.info(u"found MellonFileProviderFactory config entry with name: {}".format(d['name']))
            try:
                for f in fprovider: # iterate the files in the provider
                    if component.getUtility(mellon.IWhitelistChecker).check(f):
                        self.logger.info(u"skipping white-listed file: {}".format(f))
                        continue
                    self.logger.info(u"searching for secrets in file: {} with authorization {}".format(f, mellon.IAuthorizationContext(f)))
                    for s in f: # iterate the data snippets in the file (s provides ISnippet)
                        #App reporters should subscribe to this event feed.  Each
                        #reporter is responsible to find/execute the sniffers and
                        #also to insure whitelisted secrets are not reported on.
                        event.notify(SnippetAvailableForSecretsSniffEvent(s))
            except Exception:
                traceback.print_exc()
        self.logger.info(u"completed MellonFileProviderFactory config file entry search")

def create_and_register_app(config, verbose=False, debug=False):
    app = Mellon(verbose=verbose,debug=debug)
    app.verbose = verbose
    app.debug = debug
    if not isinstance(config, dict) and not isinstance(config, list):
        yaml_doc = component.getUtility(\
                            yaml.ISparcYamlDocuments).first(config)
        config = component.createObject(\
                                    u'sparc.configuration.container', yaml_doc)
    app.set_config(config)
    sm = component.getSiteManager()
    sm.registerUtility(app, mellon.IMellonApplication) #give components access to app config
    app.configure()
    return app

def get_registered_app():
    """Return a dict with app, config, and config value getter for currently 
    registered mellon.IMellonApplication utility
    
    Return:
        {'app':     mellon.IMellonApplication provider
         'config':  sparc.configuration.container.ISparcAppPyContainerConfiguration provider
         'vgetter': sparc.configuration.container.IPyContainerConfigValue provider
        }
    """
    app = component.getUtility(mellon.IMellonApplication)
    config = app.get_config()
    vgetter = container.IPyContainerConfigValue(config)
    return {'app':app,'config':config,'vgetter':vgetter}

def main():
    args = application.getScriptArgumentParser(DESCRIPTION).parse_args()
    create_and_register_app(args.config_file, args.verbose, args.debug)
    component.getUtility(mellon.IMellonApplication).go() #test registration and go

if __name__ == '__main__':
    main()
