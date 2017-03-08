from urllib import parse
import json
from zope import component
from zope import interface

from mellon_api import IFlaskRequest
from mellon_plugin.reporter.sqlalchemy.orm.query import ISAModelFilterExpressionGroup
from . import IAPIRequestFilter

@interface.implementer(ISAModelFilterExpressionGroup)
@component.adapter(IAPIRequestFilter)
class SAModelFilterExpressionGroupFromAPIRequestFilter(object):
    
    def __new__(self, context):
        filter_json = parse.unquote(context.filter)
        filter_container = json.loads(filter_json)
        return component.createObject(
                u"mellon_plugin.reporter.sqlalchemy.orm.query.filter_expression_group_from_container",
                filter_container)

@interface.implementer(IAPIRequestFilter)
@component.adapter(IFlaskRequest)
class APIRequestFilterFromFlaskRequest(object):
    def __init__(self, context):
        self.filter = context.args.get('filter', '')