
from pyramid.view import view_config


from pyramid.static import static_view
sb_admin_v2 = static_view('static/sb-admin-v2', use_subpath=True)

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'mellon_gui'}
