from datetime import datetime
import json
import os.path
import uuid
from zope import component
from zope import interface
from sparc.configuration import container
import mellon

from .interfaces import ISecretJsonTransformer

from sparc.logging import logging
logger = logging.getLogger(__name__)

@interface.implementer(ISecretJsonTransformer)
class DatedSecretJsonTransformer(object):
    """Return a JSON string representing a flattened secret
    
    The Jason dict structure will be:
    
        Secret JSON
        ------------
        id: unique string id for secret
        details: String details of the secret and/or how it was found
        datetime: ISO XXX formated datetime string
        snippet_data: for Unicode snippets, one or more lines of Unicode. For 
                      Byte snippets, null
        snippet_location: Description of internal file location snippet is from
        file_location: String description of where file can be located at
    
    Args:
        secret: mellon.ISecret provider
        datetime: Python datetime.datetime object that will be injected into the JSON
    
    Return:
        JSON String with above schema 
    """
    def transform(self, secret):
        snippet = secret.__parent__
        mfile = snippet.__parent__
        json_dict = {
                     'id': hash(secret),
                     'details': str(secret),
                     'datetime': datetime.utcnow().isoformat(),
                     'snippet_data': snippet.data if mellon.IUnicodeSnippet.providedBy(snippet) else None,
                     'snippet_location': snippet.__name__,
                     'file_location': str(mfile)
                     }
        return json.dumps(json_dict)
        

@component.adapter(mellon.ISecretDiscoveredEvent)
def json_reporter_for_secret(event):
    config = component.getUtility(mellon.IMellonApplication).get_config()
    MellonJsonReporter = container.IPyContainerConfigValue(config).get('MellonJsonReporter')
    json_dir = container.IPyContainerConfigValue(MellonJsonReporter).get('directory') #raises KeyError if not available
    if len(json_dir) < 2:
        raise ValueError("for safety precaution, the MellonJsonReporter.directory config entry must be greater than 1 character long.")
    if not os.path.isdir(json_dir):
        raise EnvironmentError("expected configured MellonJsonReporter.directory to exist {}".format(json_dir))
    secret_json = component.getUtility(ISecretJsonTransformer).transform(event.object)
    file_name = uuid.uuid4().hex + '.json'
    with open(os.path.join(json_dir, file_name), 'w+') as json_file:
        json_file.write(secret_json)
    
