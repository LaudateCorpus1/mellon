from zope import component
from zope import interface
import mellon

from sparc.logging import logging
logger = logging.getLogger(__name__)

@interface.implementer(mellon.IWhitelist)
@component.adapter(mellon.ISecret)
class IdWhitelistForSecret(object):
    @classmethod
    def get_ids(cls):
        config = component.getUtility(mellon.IMellonApplication).get_config()
        conf_ids = config.mapping().get_value('MellonSecretsIdWhitelist')
        ids = set()
        with open(conf_ids['file']) as f:
            for _id in [h.strip() for h in f]:
                logger.debug(u"loading id '{}' into secrets id white-list".format(_id))
                ids.add(_id)
        return ids
    ids = None
       
    def create_whitelist_info(self, _id):
        return  component.createObject(u"mellon.whitelist_info", 
                                       u"Matched secret id on {}".\
                                                format(_id))  
    
    def __init__(self, context):
        self.context = context
        if IdWhitelistForSecret.ids == None:
            logger.debug(u"secret id match file not yet loaded, initializing...")
            IdWhitelistForSecret.ids = IdWhitelistForSecret.get_ids()
            logger.debug(u"secret id match file initialization complete.")

    def __iter__(self):
        if self.context.get_id() in IdWhitelistForSecret.ids:
            yield self.create_whitelist_info(self.context.get_id())