from zope import component
from mellon_gui.interfaces import IPyramidConfigInitialized
from ..views import authenticate

@component.adapter(IPyramidConfigInitialized)
def add_route(config_inited):
    config_inited.config.add_route('login', '/login')
    config_inited.config.add_view(authenticate, route_name='login')