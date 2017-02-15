from ..testing import MellonApiRuntimeLayer
import mellon_api.auth

from sparc.logging import logging
logger = logging.getLogger(__name__)

class MellonApiAuthRuntimeLayer(MellonApiRuntimeLayer):
    
    token_lifespan = 2
    
    def setUp(self, config=None):
        _config = \
            {'MellonApiAuth':{'token':{'lifespan': self.token_lifespan}},
             'ZCMLConfiguration':
                [
                    {'package':'mellon.sniffers.test'},
                    {'package':'mellon.factories.test'},
                    {'package':'mellon.reporters.memory'},
                    {'package':'mellon_plugin.reporter.sqlalchemy.orm'},
                    {'package':'mellon_api.auth'}
                 ]
            }
        if config:
            _config.update(config)
        self.config = _config
        super(MellonApiAuthRuntimeLayer, self).setUp(config=_config)

MELLON_API_AUTH_RUNTIME_LAYER = MellonApiAuthRuntimeLayer(mellon_api.auth)