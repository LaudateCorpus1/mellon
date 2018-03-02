from zope import component
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.security import remember
from sparc.login.credentials import ICredentialsValidator

def authenticate(request):
    if 'form.submitted' in request.params:
        #first build the credentials
        identity = component.createObject(
                        u'sparc.login.credential_identity', 
                                request.params.get('username', ''))
        password = component.createObject(
                        u'sparc.login.password', 
                                request.params.get('password', ''))
        creds = component.createObject(u'sparc.login.credentials', 
                            identity=identity,
                            auth_tokens=set([password]))
        
        #now validate the credentials
        validator = component.getUtility(ICredentialsValidator, 
                                        name="sparc.login.password_validator")
        if validator.check(creds):
            headers = remember(request, identity.getId())
            return HTTPFound(location='/', headers=headers)

    return render_to_response('mellon_gui.auth.pyramid:templates/login.pt',
                              {'foo':1, 'bar':2},
                              request=request)