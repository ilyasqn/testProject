from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from configs.jwt import jwt_settings
from shared.utils import exceptions


@dataclass
class CurrentUser:
    user_id: int
    email: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/jwt/tokens")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> CurrentUser:
    try:
        payload = jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM])
    except JWTError:
        raise exceptions.UnauthorizedHTTPException()

    email: str = payload.get("email")
    user_id: int = payload.get("user_id")

    if email is None or user_id is None:
        raise exceptions.UnauthorizedHTTPException()

    return CurrentUser(user_id=user_id, email=email)
