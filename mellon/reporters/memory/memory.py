from zope import component
import mellon

from sparc.logging import logging
logger = logging.getLogger(__name__)

# keep the report here
report = []

def reset_report():
    global report
    while report:
        report.pop()

@component.adapter(mellon.ISnippetAvailableForSecretsSniffEvent)
def memory_reporter_for_secret_sniffers(event):
    global report
    for sniffer in component.subscribers((event.object,), mellon.ISecretSniffer):
        for secret in sniffer:
            if component.getUtility(mellon.IWhitelistChecker).check(secret):
                logger.info(u"skipping white-listed secret: {}".format(secret))
                continue
            logging.info(\
                u"Found secret in file snippet.  Secret information: [{}]. Snippet information: [{}].  File information: [{}].  Authorization context information [{}]"\
                .format(secret, event.object.__name__, event.object.__parent__, mellon.IAuthorizationContext(event.object)))
            report.append(secret)
