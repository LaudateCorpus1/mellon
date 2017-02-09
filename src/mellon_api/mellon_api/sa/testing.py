from zope import component
from ..testing import MellonApiRuntimeLayer
import mellon_api.sa


class MellonApiSARuntimeLayer(MellonApiRuntimeLayer):
    """GrandParent class uses the ORM layer session/engine, but in this layer,
    we have mellon_api.sa specific resources (engine/session) to clean-up
    """
    
    def setUp(self, config=None):
        super(MellonApiSARuntimeLayer, self).setUp()
    
    def tearDown(self):
        session = component.queryUtility(mellon_api.sa.ISASession)
        if session:
            session = component.getUtility(mellon_api.sa.ISASession)
            session.rollback()
            session.remove()
        super(MellonApiSARuntimeLayer, self).tearDown()

MELLON_API_SA_RUNTIME_LAYER = MellonApiSARuntimeLayer(mellon_api.sa)

class MellonApiSAExecutedLayer(MellonApiSARuntimeLayer):
    """This layer creates some DB entries from the grandfather session (and cleans them up too)
    """
    model_count = 75
    
    def setUp(self):
        super(MellonApiSAExecutedLayer, self).setUp()
        self.create_full_model(count=self.model_count)
        self.session.flush()
        #self.startApi()
    
    def tearDown(self):
        self.session.rollback()
        super(MellonApiSAExecutedLayer, self).tearDown()

MELLON_API_SA_EXECUTED_LAYER = MellonApiSAExecutedLayer(mellon_api.sa)