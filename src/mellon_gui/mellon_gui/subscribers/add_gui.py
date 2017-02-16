from zope import component
from zope.interface.interfaces import IRegistrationEvent
import mellon_api
from ..gui import gui

@component.adapter(mellon_api.IFlaskApplication, IRegistrationEvent)
def add_views(app, event):
    app.add_url_rule('/', '/', gui, methods=['GET'])