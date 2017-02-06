from zope import component
from eve import Eve
from sparc.configuration.container import application
import mellon
import mellon_api
from mellon import IMellonApplication
from mellon.mellon import create_and_register_app, get_registered_app

DESCRIPTION="""\
Mellon Restful API server.
"""

def create_eve_app():
    m = get_registered_app()
    kwargs = {}
    kwargs['settings'] = m['vgetter'].get('Eve', default={'DOMAIN':{}})
    kwargs['settings'].update(component.queryUtility(mellon_api.IEveSettings).settings)
    kwargs['auth'] = component.queryUtility(mellon_api.IEveAuthProvider)
    return Eve(**kwargs)
    

def main():
    # we'll override the core ZCML initializer with our own.
    mellon.mellon.Mellon.app_zcml = (mellon_api, 'configure.zcml')
    # create and register the Mellon app
    args = application.getScriptArgumentParser(DESCRIPTION).parse_args()
    create_and_register_app(args.config_file, args.verbose, args.debug)
    # init the runtime zcml directives
    component.getUtility(IMellonApplication).configure()
    eve_app = create_eve_app()
    eve_app.run()

if __name__ == '__main__':
    main()