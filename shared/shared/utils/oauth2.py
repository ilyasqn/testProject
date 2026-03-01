from typing import Annotated

from fastapi import Form


class OAuth2RefreshRequestForm:
    def __init__(
            self,
            *,
            grant_type: Annotated[str, Form(regex="refresh_token")],
            refresh_token: Annotated[str, Form()]
    ):
        self.grant_type = grant_type
        self.refresh_token = refresh_token
