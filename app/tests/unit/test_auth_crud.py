from dataclasses import dataclass

import pytest
from auth.models import Tokens, Users
from auth.utils.crud import (create_user, create_user_token, delete_user_by_id,
                             get_user, get_user_by_username,
                             update_user_profile)
from config.database import database
from sqlalchemy import select


@dataclass
class TestUser:
    id: int
    email: str
    username: str
    password: str
    last_name: str
    first_name: str


@pytest.mark.unit
async def test_get_user(test_data):
    user_a = await get_user(1)
    user_b = await get_user(3)

    assert user_b is None
    assert user_a.id == 1


@pytest.mark.unit
async def test_get_user_by_username(test_data):
    username_a = 'test'
    username_b = 'admin_test'

    response_a = await get_user_by_username(username_a)
    response_b = await get_user_by_username(username_b)

    assert response_a is None
    assert response_b.id == 1


@pytest.mark.unit
async def test_delete_user_by_id(test_data):
    user_id = 2

    response = await delete_user_by_id(user_id)
    expected_response = {
        'success': True, 'Message': 'User (user_id=2 has been deleted)'
    }

    query = (
        select(Users)
        .where(Users.id == user_id)
    )
    user_db = await database.fetch_one(query)

    assert user_db is None
    assert response == expected_response


@pytest.mark.unit
async def test_update_user_profile(test_data, mock_verification_email_unit):
    user = TestUser(
        id=2,
        username='test_user',
        email='user@test.com',
        last_name='last_name',
        first_name='first_test',
        password='test_password'
    )

    updated_data = {
        'email': 'updated_mail@test.com',
        'first_name': 'updated_first',
        'last_name': 'updated_last'
    }

    response = await update_user_profile(user, updated_data, 'test_url')

    expected_response = {
        'success': True, 'message': "User 'test_user' has been updated"
    }

    query = (
        select(Users)
        .where(Users.id == 2)
    )
    db_user = await database.fetch_one(query)

    assert response == expected_response
    assert db_user.email == updated_data['email']
    assert db_user.last_name == updated_data['last_name']
    assert db_user.first_name == updated_data['first_name']


@pytest.mark.unit
async def test_create_user(db_conn, mock_verification_email_unit):
    user = TestUser(
        id=1,
        username='test_user',
        email='user@test.com',
        last_name='last_name',
        first_name='first_test',
        password='test_password'
    )

    expected_response_a = {
        'success': True,
        'message': 'Verification mail has been sent (user_id=1)'
    }

    expected_response_b = {
        'success': False,
        'message': 'User creation failed. Exception: \'duplicate key value'
                   ' violates unique constraint "ix_users_email"\nDETAIL:'
                   '  Key (email)=(user@test.com) already exists.\''
    }

    response_a = await create_user(user, 'test_url')
    response_b = await create_user(user, 'test_url')

    query = (
        select(Users)
        .where(Users.id == 1)
    )

    user_db = await database.fetch_one(query)

    assert user_db.id == 1
    assert response_a == expected_response_a
    assert response_b == expected_response_b


@pytest.mark.unit
async def test_create_user_token(test_data):
    response = await create_user_token(2)

    query = (
        select(Tokens)
        .where(Tokens.user_id == 2)
    )

    token_db = await database.fetch_one(query)

    assert token_db.id == 2
    assert token_db.user_id == 2
    assert response.token == token_db.token
