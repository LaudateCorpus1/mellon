from zope import component
from zope import interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from mellon.mellon import get_registered_app
from .interfaces import IConfiguredAssignablesStatuses

@interface.implementer(IConfiguredAssignablesStatuses)
class ConfiguredAssignablesStatuses(object):
    def items(self):
        m = get_registered_app()
        terms = m['vgetter'].get('MellonWorkflowSecretAssignableStatuses')
        for t in terms:
            yield (t['value'], t['token'], t['description'])

def configuredAssignablesStatusesVocabulary():
    statuses = component.getUtility(IConfiguredAssignablesStatuses)
    return SimpleVocabulary([SimpleTerm(s[0], token=s[1], title=s[2]) \
                                                    for s in statuses.items()])
interface.alsoProvides(ConfiguredAssignablesStatuses, IVocabularyFactory)