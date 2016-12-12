from entropy import shannon_entropy
from zope import component
from zope import interface
from sparc.configuration import container
import mellon

from sparc.logging import logging
logger = logging.getLogger(__name__)

@interface.implementer(mellon.ISecretSniffer)
@component.adapter(mellon.IUnicodeSnippet)
class EntropyUnicodeSecretSniffer(object):
    
    @classmethod
    def get_config(cls):
        sm = component.getSiteManager()
        config = sm.getUtility(mellon.IMellonApplication).get_config()
        return container.IPyContainerConfigValue(config).\
                                                    get('MellonEntropySniffer')
        
    config = None
    
    def __init__(self, context):
        self.context = context
        if not EntropyUnicodeSecretSniffer.config:
            logger.debug(u"Entropy config not yet loaded, initializing...")
            EntropyUnicodeSecretSniffer.config = EntropyUnicodeSecretSniffer.get_config()
            logger.debug(u"Entropy config initialization complete.")
    
    def create_secret(self, score, matched_data):
        return  component.createObject(u"mellon.secret", 
                            name=u"Matched word entropy score {} on {}".\
                                    format(score,matched_data), 
                                parent=self.context)  
    
    def __iter__(self):
        for word in self.context.data.split():
            if self.config['word_length_min'] <= len(word) <= self.config['word_length_max']:
                logger.debug(
                    "found word ({}) that matched length constaints of min:{} and max:{}".\
                        format(word,
                               self.config['word_length_min'],
                               self.config['word_length_max']))
                if shannon_entropy(word) >= self.config['entropy_min']:
                    yield self.create_secret(shannon_entropy(word), word)