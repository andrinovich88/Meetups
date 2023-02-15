import os
from dataclasses import dataclass
from datetime import datetime

import filetype
from auth.models import Tokens, Users
from auth.utils.security import hash_password
from config.database import database
from config.settings import settings
from meetups_logging import logger
from sqlalchemy import and_, insert, join, or_, select, update


@dataclass
class VerifyUserItem:
    email_id: int | None
    username_id: int | None


async def verify_email_username(
        username: str | None, email: str | None
) -> VerifyUserItem:
    """
    Function to check availability of username and email
    :param username: Nick name in string format
    :param email: Users email address in string format
    :return: VerifyUserItem object
    """
    query_email = select(Users).where(Users.email == email)
    query_username = select(Users).where(Users.username == username)
    email = await database.fetch_one(query_email)
    username = await database.fetch_one(query_username)
    email_id = email.id if email else None
    username_id = username.id if username else None
    return VerifyUserItem(email_id=email_id, username_id=username_id)


async def create_superuser() -> None:
    """ Function for superuser creation """
    email = settings.FASTAPI_SUPERUSER_EMAIL
    username = settings.FASTAPI_SUPERUSER_NAME
    password = settings.FASTAPI_SUPERUSER_PASS

    select_query = (
        select(Users)
        .where(or_(Users.email == email,
                   Users.username == username))
    )

    admin = await database.fetch_one(select_query)

    if not admin:
        password_hash = hash_password(password)
        insert_query = (
            insert(Users)
            .values(password_hash=password_hash,
                    username=username,
                    is_active=True,
                    confirmed=True,
                    is_super=True,
                    email=email)
        )
        await database.fetch_one(insert_query)


async def activate_user(username: str) -> database:
    """
    Function to activate an existing user
    :param username: Nickname in string format
    :return: User object
    """
    query = (
        update(Users)
        .where(Users.username == username)
        .values(is_active=True, confirmed=True)
        .returning(Users.id)
    )
    return await database.fetch_one(query)


async def get_user_by_token(token: str) -> database:
    """
    Function to get the User object by token
    :param token: access token in string format
    :return: database object
    """
    query = (
        join(Tokens, Users).select().where(
            and_(
                Tokens.token == token,
                Tokens.expires > datetime.now()
            )
        )
    )
    return await database.fetch_one(query)


def verify_avatar_image(file: bytes) -> bool:
    """
    Function for upload file type validation
    :param file: file content in bytes format
    :return: boolean statement. True if file content is image False in
             another case
    """
    if filetype.is_image(file):
        return True
    return False


async def update_avatar_url_in_db(url: str, user_id: int) -> None:
    """
    Function for updating avatar_url field in database
    :param url: path to user's avatar image
    :param user_id: user's ID in integer format
    """
    query = (
        update(Users)
        .where(Users.id == user_id)
        .values(avatar_url=url)
    )
    await database.fetch_one(query)


async def save_avatar_image(file_content: bytes, user_id: int) -> dict:
    """
    Function for dumping user avatar image on a hard disk surface
    :param file_content: content of file in bytes format
    :param user_id: user's ID in integer format
    :return: Path to a user avatar image
    """
    base_path = f"storage/{user_id}/images"
    file_path = f"{base_path}/avatar.jpg"

    try:
        os.makedirs(base_path, exist_ok=True)
        with open(file_path, 'wb') as file:
            file.write(file_content)
    except Exception as e:
        logger.error(str(e))
        return {
            "success": False,
            "message": f"Writing the file to disk failed. Exception: "
                       f"'{str(e)}'"
        }

    try:
        await update_avatar_url_in_db(url=file_path, user_id=user_id)
    except Exception as e:
        logger.error(str(e))
        return {
            "success": False,
            "message": f"Updating a record in the database failed. Exception:"
                       f" '{str(e)}'"
        }

    return {
        "success": True,
        "message": f"User avatar upload successful (user_id = {user_id})"
    }
