from passlib.context import CryptContext

user_password_crypt_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")