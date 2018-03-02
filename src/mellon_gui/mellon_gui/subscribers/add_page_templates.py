from pyramid.renderers import get_renderer

def add_main_template(render_dict):
    """See http://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/templates/templates.html#using-a-beforerender-event-to-expose-chameleon-base-template
    """
    #render_dict is a dict that is exposed to chameleon page templates.  We 
    #populate it with the main template to allow other page templates to access
    #and leverage it.
    main = get_renderer('mellon_gui:templates/main.pt').implementation()
    render_dict.update({'main': main})