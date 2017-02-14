from zope import interface
from .interfaces import IFlaskRestApiPostprocessors
from .interfaces import IFlaskRestApiPreprocessors

class FlaskRestApiProcessor(dict):
    """wrapper class for a Flask Rest api pre/post processor definition"""

preprocessors_default = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors_default, IFlaskRestApiPreprocessors)

postprocessors_default = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors_default, IFlaskRestApiPostprocessors)

preprocessors_secret = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors_secret, IFlaskRestApiPreprocessors)

postprocessors_secret = FlaskRestApiProcessor()
interface.alsoProvides(postprocessors_secret, IFlaskRestApiPostprocessors)