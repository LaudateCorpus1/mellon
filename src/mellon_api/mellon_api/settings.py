from zope import interface
from zope.component.factory import Factory
from . import IEveSettings

@interface.implementer(IEveSettings)
class EveSettings(object):
    def __init__(self, settings):
        self.settings = settings
eveSettingsFactory = Factory(EveSettings)

default_eve_settings = EveSettings(settings={
'DOMAIN': {}
})