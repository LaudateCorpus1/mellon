from zope import component
from zope import interface
from . import IUserPasswordAuthenticationManager, ICryptContext, models, exc
from ..sa import ISASession

@interface.implementer(IUserPasswordAuthenticationManager)
@component.adapter(ISASession)
class UserPasswordAuthenticationManager(object):
    
    def __init__(self, context):
        self.context = context
        self.session = context
        self.crypt = component.getUtility(ICryptContext, name=u"mellon_api.auth.user_password_crypt_context")
    
    def _get_username(self, username):
        Usr = models.UserPasswordAuthentication
        user = self.session.query(Usr).filter(Usr.username == username).first()
        if not user:
            raise KeyError("specified username does not exist")
        return user

    def _get_principal(self, principal_id):
        principal = self.session.query(models.Principal).\
                    filter(models.Principal.id == principal_id).first()
        if not principal:
            raise KeyError("specified principal does not exist")
        return principal

    def create(self, username, password, principal_id=None):
        
        try:
            self._get_username(username)
            raise ValueError(u"specified username already exists")
        except KeyError:
            pass
        if not principal_id:
            prncpl = models.Principal()
            self.session.add(prncpl)
            self.session.flush() #generates the principal id
        else:
            prncpl = self._get_principal(principal_id)
        user = models.UserPasswordAuthentication(username=username, 
                   password_crypt=self.crypt.hash(password),
                   principal_id=prncpl.id)
        self.session.add(user)
        return user

    def check_authentication(self, username, password):
        user = self._get_username(username)
        if not user.password_crypt:
            raise exc.MellonAPIUserIsDisabled()
        if not self.crypt.verify(password, user.password_crypt):
            raise exc.MellonAPIInvalidPassword()
    
    def update_password(self, username, password):
        user = self._get_username(username)
        user.password_crypt = self.crypt.hash(password)
        
    def update_username(self, username, new):
        user = self._get_username(username)
        try:
            self._get_username(new)
        except KeyError:
            user.username = new
            return
        raise ValueError(u"specified new username already exists")
    
    def disable(self, username):
        user = self._get_username(username)
        user.password_crypt = None
    
    def delete(self, username):
        user = self._get_username(username)
        self.session.delete(user)
        