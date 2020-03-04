from zope import component
from zope import interface

from mellon.mellon import get_registered_app
from .interfaces import IConfiguredAssignablesStatuses

@interface.implementer(IConfiguredAssignablesStatuses)
class ConfiguredAssignablesStatuses(object):
    def items(self):
        m = get_registered_app()
        terms = m['vgetter'].get_value('MellonWorkflowSecretAssignableStatuses')
        for t in terms:
            yield (t['value'], t['token'], t['description'])
