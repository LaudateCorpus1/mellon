from zope import interface

from mellon.mellon import get_registered_app
from .interfaces import IConfiguredAssignablesSeverities

@interface.implementer(IConfiguredAssignablesSeverities)
class ConfiguredAssignablesSeverities(object):
    def items(self):
        m = get_registered_app()
        terms = m['vgetter'].get_value('MellonWorkflowSecretAssignableSeverities')
        for t in terms:
            yield (t['value'], t['token'], t['description'])
