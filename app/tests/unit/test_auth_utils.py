import os

import pytest
from auth.models import Users
from auth.utils.auth_utils import (VerifyUserItem, activate_user,
                                   create_superuser, get_user_by_token,
                                   save_avatar_image, update_avatar_url_in_db,
                                   verify_avatar_image, verify_email_username)
from config.database import database
from sqlalchemy import select


@pytest.mark.unit
async def test_verify_email_username(test_data):
    data_a = {'username': 'test_user', 'email': 'test_mail@test.com'}
    data_b = {'username': 'test_user', 'email': 'test@gmail.com'}
    data_c = {'username': 'admin_test', 'email': 'test_mail@test.com'}

    response_a = await verify_email_username(**data_a)
    response_b = await verify_email_username(**data_b)
    response_c = await verify_email_username(**data_c)

    expected_response_a = VerifyUserItem(email_id=None, username_id=None)
    expected_response_b = VerifyUserItem(email_id=1, username_id=None)
    expected_response_c = VerifyUserItem(email_id=None, username_id=1)

    assert response_a == expected_response_a
    assert response_b == expected_response_b
    assert response_c == expected_response_c


@pytest.mark.unit
async def test_create_superuser(db_conn):
    await create_superuser()
    await create_superuser()

    query = (
        select(Users)
        .where(Users.is_super)
    )

    users_db = await database.fetch_all(query)

    assert len(users_db) == 1
    assert users_db[0].is_super
    assert users_db[0].confirmed
    assert users_db[0].is_active


@pytest.mark.unit
async def test_activate_user(test_data):
    response = await activate_user('user_test')

    query = (
        select(Users)
        .where(Users.id == response.id)
    )

    result = await database.fetch_one(query)

    assert result.is_active
    assert result.confirmed


@pytest.mark.unit
async def test_get_user_by_token(test_data):
    response_a = await get_user_by_token(
        '2ec64c1f-de97-4e86-808c-34a48bb7840a'
    )
    response_b = await get_user_by_token(
        '2ec64c1f-de97-4e86-808c-34a48bb7840b'
    )

    assert response_a.id == 1
    assert response_b is None


@pytest.mark.unit
def test_verify_avatar_image():
    with open("./tests/files/test_image.png", 'rb') as file:
        file_a = file.read()

    file_b = b'Hello world'

    response_a = verify_avatar_image(file_a)
    response_b = verify_avatar_image(file_b)

    assert response_a is True
    assert response_b is False


@pytest.mark.unit
async def test_update_avatar_url_in_db(test_data):
    url = 'test_url'
    await update_avatar_url_in_db(url, 2)

    query = (
        select(Users)
        .where(Users.id == 2)
    )

    user_db = await database.fetch_one(query)

    assert user_db.avatar_url == 'test_url'


@pytest.mark.unit
async def test_save_avatar_image(db_conn):
    with open("./tests/files/test_image.png", 'rb') as file:
        content = file.read()

    response = await save_avatar_image(content, 1)

    expected_response = {
        'success': True,
        'message': 'User avatar upload successful (user_id = 1)'
    }

    with open("./storage/1/images/avatar.jpg", 'rb') as file:
        saved_content = file.read()

    assert response == expected_response
    assert content == saved_content

    os.remove("./storage/1/images/avatar.jpg")
