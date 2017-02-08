from zope import component
from ..testing import MellonApiRuntimeLayer
from mellon_api.sa import ISASession
import mellon_api


class MellonApiSARuntimeLayer(MellonApiRuntimeLayer):
    """GrandParent class uses the ORM layer session/engine, but in this layer,
    we have mellon_api.sa specific resources (engine/session) to clean-up
    """
    
    def setUp(self, config=None):
        super(MellonApiSARuntimeLayer, self).setUp()
    
    def tearDown(self):
        session = component.getUtility(ISASession)
        session.rollback()
        session.remove()
        super(MellonApiSARuntimeLayer, self).tearDown()

MELLON_API_SA_RUNTIME_LAYER = MellonApiSARuntimeLayer(mellon_api)