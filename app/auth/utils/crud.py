from datetime import datetime, timedelta
from uuid import uuid4

from auth import schemas as user_schema
from auth.models import Tokens, Users
from auth.utils.mail import generate_html_message
from auth.utils.security import hash_password
from celery_tasks.tasks import send_verification_email_celery
from config.database import database
from meetups_logging import logger
from sqlalchemy import delete, insert, select, update


async def get_user(user_id: int) -> database:
    """
    Function for getting User object by ID
    :param user_id: user id in integer format
    :return: User object
    """
    query = select(Users).where(Users.id == user_id)
    return await database.fetch_one(query)


async def get_user_by_username(username: str) -> database:
    """
    Function for getting User object by username
    :param username: User nickname in string format
    :return: User database object
    """
    query = select(Users).where(Users.username == username)
    return await database.fetch_one(query)


async def delete_user_by_id(user_id: int) -> dict:
    """
    Function for removal existing user and user's access tokens
    :param user_id: User id in integer format
    """
    query = delete(Users).where(
        Users.id == user_id
    )
    try:
        await database.fetch_one(query)
    except Exception as e:
        logger.error(str(e))
        return {
            "success": False,
            "message": f"User removal failed (user_id={user_id}). Exception: "
                       f"'{str(e)}'"
        }
    return {
        "success": True,
        "Message": f"User (user_id={user_id} has been deleted)"
    }


async def update_user_profile(
        current_user: user_schema.User, updated_data: dict, base_url: str
) -> dict:
    """
    Function for partial update User object
    :param current_user: Authenticated User object
    :param updated_data: Data to update
    :param base_url: Parent URL for composing a confirmation letter
    :return: User object or None
    """
    values = dict()
    query = (
        update(Users)
        .where(Users.id == current_user.id)
        .returning(Users.id)
    )

    if updated_data.get("password"):
        values['password_hash'] = hash_password(updated_data["password"])

    if updated_data.get("first_name"):
        values['first_name'] = updated_data["first_name"]

    if updated_data.get("last_name"):
        values['last_name'] = updated_data["last_name"]

    if updated_data.get("email"):
        values.update(
            {
                'email': updated_data["email"],
                'confirmed': False,
                'is_active': False
            }
        )

    if values:
        try:
            await database.fetch_one(query=query, values=values)
            if values.get('email'):
                message = generate_html_message(
                    username=current_user.username, base_url=base_url
                )
                send_verification_email_celery.apply_async(
                    args=[updated_data["email"], message]
                )
        except Exception as e:
            logger.error(str(e))
            return {
                "success": False,
                "message": f"User update failed (user_id={current_user.id}"
                           f"). Exception: {str(e)}"
            }
        return {
            "success": True,
            "message": f"User '{current_user.username}' has been updated"
        }


async def create_user(
        user: user_schema.UserCreate, base_url: str
) -> dict:
    """
    Function for new user creation
    :param user: User form data
    :param base_url: Parent URL for composing a confirmation letter
    :return: User object
    """
    query = (
        insert(Users)
        .values(email=user.email,
                username=user.username,
                last_name=user.last_name,
                first_name=user.first_name,
                password_hash=hash_password(user.password),
                )
        .returning(Users.id, Users.email, Users.username)
    )
    try:
        user = await database.fetch_one(query)
        await create_user_token(user.id)
        message = generate_html_message(
            username=user.username, base_url=base_url
        )
        send_verification_email_celery.apply_async(
            args=[user.email, message]
        )
    except Exception as e:
        logger.error(str(e))
        return {
            "success": False,
            "message": f"User creation failed. Exception: '{str(e)}'"
        }
    return {
        "success": True,
        "message": f"Verification mail has been sent (user_id={user.id})"
    }


async def create_user_token(user_id: int) -> database:
    """
    Function for new access token creation
    :param user_id: User object ID
    :return: Tokens object
    """
    query = (
        insert(Tokens)
        .values(
            token=uuid4(),
            expires=datetime.now() + timedelta(weeks=2),
            user_id=user_id)
        .returning(Tokens.token, Tokens.expires)
    )

    return await database.fetch_one(query)
