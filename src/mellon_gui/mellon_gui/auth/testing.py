from ..testing import MellonWebAppRuntimeLayer
import mellon_gui.auth

from sparc.logging import logging
logger = logging.getLogger(__name__)

class MellonWebAppAuthRuntimeLayer(MellonWebAppRuntimeLayer):
    
    token_lifespan = 2
    
    def setUp(self, config=None):
        _config = \
            {'PyramidAuthTktAuthenticationPolicy':
                 {'secret': 'test_secret'},
             'ZCMLConfiguration':
                [
                    {'package':'mellon.sniffers.test'},
                    {'package':'mellon.factories.test'},
                    {'package':'mellon.reporters.memory'},
                    {'package':'mellon_plugin.reporter.sqlalchemy.orm'},
                    {'package':'mellon_gui.auth'}
                 ]
            }
        if config:
            _config.update(config)
        self.config = _config
        super(MellonWebAppAuthRuntimeLayer, self).setUp(config=_config)

MELLON_WEB_APP_AUTH_RUNTIME_LAYER = MellonWebAppAuthRuntimeLayer(mellon_gui.auth)