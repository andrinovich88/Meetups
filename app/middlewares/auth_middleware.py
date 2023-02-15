from dataclasses import dataclass
from typing import Optional, Tuple

from auth.utils.auth_utils import get_user_by_token
from starlette.authentication import AuthenticationBackend
from starlette.requests import HTTPConnection


@dataclass
class AuthUser:
    id: int
    is_super: bool
    is_active: bool
    confirmed: bool


class AuthMiddleware(AuthenticationBackend):
    """

     Auth backend based on  Starlette's AuthenticationBackend

    """

    async def authenticate(
            self, connection: HTTPConnection
    ) -> Tuple[bool, Optional[AuthUser]]:
        auth = connection.headers.get("Authorization")

        if not auth or "bearer" not in auth.lower():
            return False, None

        scheme, _, credentials = auth.partition(" ")
        user = await get_user_by_token(credentials)

        if not user:
            return False, None

        return True, AuthUser(id=user.user_id,
                              is_super=user.is_super,
                              is_active=user.is_active,
                              confirmed=user.confirmed)
