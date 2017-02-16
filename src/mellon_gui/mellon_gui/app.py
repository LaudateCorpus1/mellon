import os
from zope import component
from sparc.configuration.container import application
import mellon
import mellon_api
import mellon_gui
from mellon.mellon import get_registered_app
from mellon_api.app import create_and_register_app, register_flask_app, configure_flask_app

DESCRIPTION="""\
Mellon GUI Web server.
"""

def main():
    args = application.getScriptArgumentParser(DESCRIPTION).parse_args()
    # we'll override the core ZCML initializer with our own. then create the
    # base mellon application and init the component registry with the 
    # yaml-based zcml entry points
    mellon.mellon.Mellon.app_zcml = (mellon_gui, 'configure.zcml')
    create_and_register_app(args.config_file, args.verbose, args.debug)
    component.getUtility(mellon.IMellonApplication).configure()
    #create, register, and run the application
    m = get_registered_app() # the Mellon application
    if 'Flask' not in m['config']:
        m['config']['Flask'] = component.createObject(u"sparc.configuration.container", {'kwargs':{}})
    if 'kwargs' not in m['config']['Flask']:
        m['config']['Flask']['kwargs'] = component.createObject(u"sparc.configuration.container", {})
    
    static_path = os.path.join(os.path.dirname(mellon_gui.__file__),'ember','mellon','dist')
    m['config']['Flask']['kwargs']['static_folder'] = static_path
    
    register_flask_app()
    configure_flask_app()
    component.getUtility(mellon_api.IFlaskApplication).run()

if __name__ == '__main__':
    main()