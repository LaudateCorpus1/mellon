from zope import component
from sparc.configuration.container import application
import mellon
import mellon_api
import mellon_gui
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
    register_flask_app()
    configure_flask_app()
    component.getUtility(mellon_api.IFlaskApplication).run()

if __name__ == '__main__':
    main()