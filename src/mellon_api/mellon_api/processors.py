from zope import interface
#from .interfaces import IFlaskRestApiPostprocessors
from .interfaces import IFlaskRestApiPreprocessors

class FlaskRestApiProcessor(list):
    """wrapper class for a Mellon Rest api pre/post processor definition"""

preprocessors = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors, IFlaskRestApiPreprocessors)

"""
preprocessors_global = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors_global, IFlaskRestApiPreprocessors)

postprocessors_global = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors_global, IFlaskRestApiPostprocessors)

preprocessors_secret = FlaskRestApiProcessor()
interface.alsoProvides(preprocessors_secret, IFlaskRestApiPreprocessors)

postprocessors_secret = FlaskRestApiProcessor()
interface.alsoProvides(postprocessors_secret, IFlaskRestApiPostprocessors)
"""