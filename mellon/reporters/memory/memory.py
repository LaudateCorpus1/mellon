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
            wht_lstd = False
            for wht_lst in component.subscribers((secret,), mellon.IWhitelist):
                for wht_lst_info in wht_lst:
                    logger.info(u"skipping white-listed secret: {} because {}".format(secret, wht_lst_info))
                    wht_lstd = True
            if not wht_lstd:
                logging.info(\
                    u"Found secret in file snippet.  Secret information: [{}]. Snippet information: [{}].  File information: [{}]."\
                    .format(secret, event.object.__name__, event.object.__parent__))
                report.append(secret)
