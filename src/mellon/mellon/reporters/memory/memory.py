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

@component.adapter(mellon.ISecretDiscoveredEvent)
def memory_reporter_for_secret(event):
    global report
    logger.debug('appending secret to module-level report list')
    report.append(event.object)
