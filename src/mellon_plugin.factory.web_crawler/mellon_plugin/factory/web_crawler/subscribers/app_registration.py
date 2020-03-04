from zope import component
import mellon

from sparc.logging import logging
logger = logging.getLogger(__name__)

@component.adapter(mellon.IMellonApplication, mellon.IMellonApplicationConfiguredEvent)
def initialize_spiders(app, event):
    """Register configured storage facility"""
    if app.get_config().mapping().query_value('ScrapySimpleTextWebsiteCrawler'):
        import mellon_plugin.factory.web_crawler.web_crawler.spiders.config_spiders
