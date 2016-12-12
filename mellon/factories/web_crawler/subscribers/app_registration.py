from zope import component
from sparc import configuration
from sparc.configuration import container
import mellon

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(mellon.IMellonApplication, configuration.ISparcApplicationConfiguredEvent)
def initialize_spiders(app, event):
    """Register configured reaper storage facility"""
    if container.IPyContainerConfigValue(app.get_config()).\
                                        query('ScrapySimpleTextWebsiteCrawler'):
        import mellon.factories.web_crawler.web_crawler.spiders.config_spiders
