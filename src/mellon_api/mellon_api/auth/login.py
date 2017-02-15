from werkzeug.exceptions import Unauthorized
from flask import jsonify
from zope import component
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mellon.mellon import get_registered_app
from . import exc
from . import IUserPasswordAuthenticationManager
from .. import IFlaskRequest, IFlaskApplication
from ..sa import ISASession


def login(**kwargs):
    manager = IUserPasswordAuthenticationManager(
                            component.getUtility(ISASession))
    r = component.getUtility(IFlaskRequest).request
    try:
        manager.check_authentication(r.form['username'], r.form['password'])
    except (KeyError, exc.MellonAPIAuthenticationException):
        raise Unauthorized('invalid authentication supplied.')
    m = get_registered_app()
    
    app = component.getUtility(IFlaskApplication)
    lifespan = m['vgetter'].get('MellonApiAuth','token','lifespan', default=86400)
    
    s = Serializer(app.config['SECRET_KEY'], expires_in=lifespan)
    token = s.dumps({'username': r.form['username']})
    return jsonify({'token': token.decode('ascii')})