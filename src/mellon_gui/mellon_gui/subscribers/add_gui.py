from zope import component
from zope.interface.interfaces import IRegistrationEvent
import mellon_api
from ..gui import gui, static_proxy

@component.adapter(mellon_api.IFlaskApplication, IRegistrationEvent)
def add_views(app, event):
    app.add_url_rule('/', 'index', gui, methods=['GET'])
    app.add_url_rule('/<path:path>', 'static_proxy', static_proxy, methods=['GET'])