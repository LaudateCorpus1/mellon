from zope import component
from mellon_api import IFlaskApplication


def gui():
    #return 'hello world'
    app = component.getUtility(IFlaskApplication)
    return app.send_static_file('index.html')

def static_proxy(path):
    app = component.getUtility(IFlaskApplication)
    return app.send_static_file(path)