from passlib.context import CryptContext


class PasswordUtils:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def _verify_password(cls, plain_password, hashed_password):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def _get_password_hash(cls, password):
        return cls.pwd_context.hash(password)
