from zope import interface
from .interfaces import IFlaskRestApiPostprocessors
from .interfaces import IFlaskRestApiPreprocessors

class FlaskRestApiProcessor(dict):
    """wrapper class for a Flask Rest api pre/post processor definition"""

preprocessors_global = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors_global, IFlaskRestApiPreprocessors)

postprocessors_global = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors_global, IFlaskRestApiPostprocessors)

preprocessors_secret = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors_secret, IFlaskRestApiPreprocessors)

postprocessors_secret = FlaskRestApiProcessor()
interface.alsoProvides(postprocessors_secret, IFlaskRestApiPostprocessors)