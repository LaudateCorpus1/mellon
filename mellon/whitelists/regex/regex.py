from zope import component
from zope import interface
from sparc.configuration import container
import mellon
import re

from sparc.logging import logging
logger = logging.getLogger(__name__)
sm = component.getSiteManager()

@interface.implementer(mellon.IWhitelist)
class RegExWhitelistMixin(object):
    @classmethod
    def get_patterns(cls):
        config = sm.getUtility(mellon.IMellonApplication).get_config()
        conf_regex = container.IPyContainerConfigValue(config).\
                                                    get('MellonRegexWhitelist')
        
        patterns = {'all': [], 'file': [], 'secret':[]} #list of dicts
        for type_ in patterns.keys():
            if type_ in conf_regex['pattern_files']:
                logger.debug(u"found pattern file {}, looking for regex patterns to load ...".format(conf_regex['pattern_files'][type_]))
                with open(conf_regex['pattern_files'][type_]) as f:
                    for pattern in f:
                        types = [type_] if type_ in ('file', 'secret', ) else ['file', 'secret']
                        for t in types:
                            logger.debug(u"loading pattern '{}' into {} Regex white-list".format(pattern, t))
                            patterns[t].append({'pattern': pattern,
                                                'prog':re.compile(pattern)})
        return patterns
    patterns = None   
       
    def create_whitelist_info(self, pattern, matched_data):
        return  component.createObject(u"mellon.whitelist_info", 
                                       u"Matched regex pattern {} on {}".\
                                                format(pattern,matched_data))            
    
    def __init__(self, context):
        self.context = context
        if not RegExWhitelistMixin.patterns:
            logger.debug(u"Regex pattern files not yet loaded, initializing...")
            RegExWhitelistMixin.patterns = RegExWhitelistMixin.get_patterns()
            logger.debug(u"Regex pattern file initialization complete.")

@component.adapter(mellon.IMellonFile)
class RegExWhitelistForMellonFile(RegExWhitelistMixin):
    def __iter__(self):
        for entry in self.patterns['file']:
            match = entry['prog'].search(str(self.context))
            if match:
                yield self.create_whitelist_info(entry['pattern'],match.group(0))

@component.adapter(mellon.ISecret)
class RegExWhitelistForSecret(RegExWhitelistMixin):
    def __iter__(self):
        for entry in self.patterns['secret']:
            match = entry['prog'].search(str(self.context))
            if match:
                yield self.create_whitelist_info(entry['pattern'],match.group(0))
