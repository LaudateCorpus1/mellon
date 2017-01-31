from zope import component
from zope import interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from mellon.mellon import get_registered_app
from .interfaces import IConfiguredAssignablesSeverities

@interface.implementer(IConfiguredAssignablesSeverities)
class ConfiguredAssignablesSeverities(object):
    def items(self):
        m = get_registered_app()
        terms = m['vgetter'].get('MellonWorkflowSecretAssignableSeverities')
        for t in terms:
            yield (t['value'], t['token'], t['description'])

def configuredAssignablesSeveritiesVocabulary():
    statuses = component.getUtility(IConfiguredAssignablesSeverities)
    return SimpleVocabulary([SimpleTerm(s[0], token=s[1], title=s[2]) \
                                                    for s in statuses.items()])
interface.alsoProvides(configuredAssignablesSeveritiesVocabulary, IVocabularyFactory)