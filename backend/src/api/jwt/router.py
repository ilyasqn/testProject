from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.services.user.auth import AuthService
from src.utils.oauth2 import OAuth2RefreshRequestForm

router = APIRouter(
    prefix='/jwt',
    tags=['jwt']
)


@router.post(
    path="/tokens",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {
                    "example": {
                        "token_type": "Bearer",
                        "access_token": "eyJhbGciOiJIUzI1NiIkpXVCJ9.eyJlbW...",
                        "access_token_exp": "datetime",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIpXVCJ9.eyJlbW...",
                        "refresh_token_exp": "datetime",
                    }
                }
            },
        },
    })
async def login_for_tokens(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await AuthService.authenticate(
        email=form_data.username,
        password=form_data.password
    )
    (
        token_type, access_token, access_token_exp,
        refresh_token, refresh_token_exp
    ) = AuthService.create_tokens({"email": user.email})
    return {
        "token_type": token_type,
        "access_token": access_token,
        "access_token_exp": access_token_exp,
        "refresh_token": refresh_token,
        "refresh_token_exp": refresh_token_exp
    }


@router.post(
    path='/refresh_token',
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {
                    "example": {
                        "token_type": "Bearer",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5J9.eyJlbW...",
                        "access_token_exp": "datetime",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIpXVCJ9.eyJlbW...",
                        "refresh_token_exp": "datetime",
                    }
                }
            },
        },
    })
async def get_refresh_token(
    form_data: Annotated[OAuth2RefreshRequestForm, Depends()]
):
    user = await AuthService.authenticate_by_token(form_data.refresh_token)
    (
        token_type, access_token, access_token_exp,
        refresh_token, refresh_token_exp
    ) = AuthService.create_tokens({"email": user.email})
    return {
        "token_type": token_type,
        "access_token": access_token,
        "access_token_exp": access_token_exp,
        "refresh_token": refresh_token,
        "refresh_token_exp": refresh_token_exp
    }