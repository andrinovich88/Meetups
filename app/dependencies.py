from dataclasses import dataclass

from auth.utils import auth_utils
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/sign_in")


@dataclass
class UserItem:
    id: int
    email: str
    username: str
    is_super: bool
    last_name: str | None
    first_name: str | None
    avatar_url: str | None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserItem:
    """
    Function for getting active current user. Used for user authorization
    :param token: access token in string format
    :return: dict with active user data
    """
    user = await auth_utils.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user["is_active"] or not user["confirmed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return UserItem(
        id=user.user_id,
        email=user.email,
        is_super=user.is_super,
        username=user.username,
        last_name=user.last_name,
        first_name=user.first_name,
        avatar_url=user.avatar_url,
    )


async def superuser_required(request: Request) -> bool:
    """ Function for checking superuser status """
    if not request.user.is_super:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "message": "Current user is not a superuser"
            }
        )
    return True
