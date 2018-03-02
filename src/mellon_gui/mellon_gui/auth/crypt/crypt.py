from zope import interface
from passlib.context import CryptContext
from sparc.login.credentials.authn.crypt import ICrypter

user_password_crypt_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
interface.alsoProvides(user_password_crypt_context, ICrypter)