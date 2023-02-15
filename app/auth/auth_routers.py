from auth.schemas import (SimpleMessage, TokenBase, User, UserCreate,
                          UserProfile, UserUpdate)
from auth.utils import auth_utils
from auth.utils.crud import (create_user, create_user_token, delete_user_by_id,
                             get_user_by_username, update_user_profile)
from auth.utils.security import (check_strong_password, decode_jwt_token,
                                 validate_password)
from dependencies import get_current_user
from fastapi import APIRouter, Depends, File, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from meetups_logging import logger
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/profile/", response_model=UserProfile)
async def view_profile(current_user: User = Depends(get_current_user)):
    """ The API endpoint for browsing user profile """
    return current_user


@router.delete("/delete_user/", response_model=SimpleMessage)
async def delete_profile(current_user: User = Depends(get_current_user)):
    """ The API endpoint for user profile removal """
    result = await delete_user_by_id(user_id=current_user.id)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result)

    return JSONResponse(status_code=200, content=result)


@router.put("/edit_profile/", response_model=SimpleMessage)
async def edit_profile(
        user: UserUpdate, request: Request,
        current_user: User = Depends(get_current_user)
):
    """ The API endpoint for editing user profile """
    unique_values = set(dict(user).values())

    if None in unique_values and len(unique_values) == 1:
        msg = {"success": False, "message": "No data to update"}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    if user.email:
        db_user = await auth_utils.verify_email_username(
            username=None, email=user.email
        )
        if db_user.email_id:
            msg = {"success": False, "message": "Email already registered"}
            logger.warning(msg)
            raise HTTPException(status_code=400, detail=msg)

    if user.password:
        password_error = check_strong_password(user.password)
        if password_error:
            msg = {"success": False, "message": password_error}
            logger.warning(msg)
            raise HTTPException(status_code=400, detail=msg)

    result = await update_user_profile(
        updated_data=user.dict(),
        current_user=current_user,
        base_url=str(request.base_url),
    )
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result)

    return JSONResponse(status_code=200, content=result)


@router.post("/sign_up/", response_model=SimpleMessage)
async def sign_up(user: UserCreate, request: Request):
    """ The API endpoint for new user creation """
    db_user = await auth_utils.verify_email_username(
        username=user.username,
        email=user.email
    )
    password_error = check_strong_password(user.password)

    if password_error:
        msg = {"success": False, "message": password_error}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    if db_user.email_id and db_user.username_id:
        msg = {"success": False, "message": "User already registered"}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    elif db_user.email_id:
        msg = {"success": False, "message": "Email already registered"}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    elif db_user.username_id:
        msg = {"success": False, "message": "Username already registered"}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    result = await create_user(user=user, base_url=str(request.base_url))
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result)

    return JSONResponse(status_code=201, content=result)


@router.post("/upload_avatar", response_model=SimpleMessage)
async def upload_avatar(
        current_user: User = Depends(get_current_user),
        avatar_image: bytes = File(
            title='avatar image'
        )
):
    """ The API endpoint for uploading users avatars """
    is_image = auth_utils.verify_avatar_image(avatar_image)
    if not is_image:
        msg = {"success": False, "message": "Incorrect file type"}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    result = await auth_utils.save_avatar_image(
        avatar_image, current_user.id
    )
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result)

    return JSONResponse(status_code=201, content=result)


@router.get("/activate_user/{token}", include_in_schema=False,
            response_model=SimpleMessage)
async def activate_user(token: str):
    """ The endpoint for user activation. Used to process GET requests for
        links from verification emails."""
    try:
        username = decode_jwt_token(token)
    except JWTError:
        msg = {"success": False, "message": "Incorrect validation token"}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    user = await auth_utils.activate_user(username)
    if not user:
        msg = {"success": False, "message": "Incorrect validation token"}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    return {
        "success": True,
        "message": f"User '{username}' has been activated"
    }


@router.post("/sign_in/", include_in_schema=False, response_model=TokenBase)
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends()):
    """ The endpoint for checking user credential.
        Used to authenticate users. """
    user = await get_user_by_username(username=form_data.username)
    if not user:
        msg = {"success": False, "message": "Incorrect email or password"}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    if not validate_password(
            password=form_data.password,
            hashed_password=user["password_hash"]
    ):
        msg = {"success": False, "message": "Incorrect email or password"}
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    return await create_user_token(user_id=user["id"])
