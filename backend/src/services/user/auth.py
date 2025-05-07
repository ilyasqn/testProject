import datetime
from typing import Annotated, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.utils.password import PasswordUtils
from configs.jwt import jwt_settings
from src.repositories.user import UserRepository
from src.schemas.user import UserSchemaRead, UserSchemaReadWithPassword
from src.utils import exceptions
from src.db.db import async_session_maker


class AuthService:
    oauth2_password_scheme = OAuth2PasswordBearer(tokenUrl="/api/jwt/tokens")
    token_type = 'Bearer'

    @classmethod
    async def get_current_user(cls, token: Annotated[str, Depends(oauth2_password_scheme)]) -> UserSchemaRead:
        return await cls.authenticate_by_token(token)

    @classmethod
    async def authenticate_by_refresh_token(cls, token: str, grant_type: str) -> UserSchemaRead:
        if grant_type != 'refresh_token':
            raise exceptions.UnauthorizedHTTPException(
                detail="Expected 'grant_type' parameter with 'refresh_token' value")
        return await cls.authenticate_by_token(token)

    @classmethod
    async def authenticate_by_token(cls, token: str) -> UserSchemaRead:
        try:
            payload = jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=jwt_settings.ALGORITHM)
        except JWTError:
            raise exceptions.UnauthorizedHTTPException()
        email: str = payload.get("email")
        if email is None:
            raise exceptions.UnauthorizedHTTPException()
        users_repo = UserRepository(async_session_maker())
        user = await users_repo.get_one(email=email)
        if user is None:
            raise exceptions.UnauthorizedHTTPException()
        await users_repo.session.commit()
        return UserSchemaRead.model_validate(user, from_attributes=True)

    @classmethod
    async def authenticate(cls, email: str,
                           password: str) -> UserSchemaReadWithPassword:
        users_repo = UserRepository(async_session_maker())
        user = await users_repo.get_one(email=email)
        if user is None:
            raise exceptions.UnauthorizedHTTPException(detail="Incorrect email or password")
        if not PasswordUtils._verify_password(password, user.password):
            raise exceptions.UnauthorizedHTTPException(detail="Incorrect email or password")
        await users_repo.session.commit()
        return UserSchemaReadWithPassword.model_validate(user, from_attributes=True)

    @classmethod
    def create_tokens(cls,
                      data: dict,
                      ) -> tuple[str, str, datetime.datetime, str, datetime.datetime]:
        now = datetime.datetime.utcnow()

        access_token_exp = now + datetime.timedelta(minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = data.copy()
        to_encode["exp"] = access_token_exp
        access_token = jwt.encode(to_encode, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)

        refresh_token_exp = now + datetime.timedelta(hours=jwt_settings.REFRESH_TOKEN_EXPIRE_HOURS)
        to_encode = data.copy()
        to_encode["exp"] = refresh_token_exp
        refresh_token = jwt.encode(to_encode, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)

        return cls.token_type, access_token, access_token_exp, refresh_token, refresh_token_exp