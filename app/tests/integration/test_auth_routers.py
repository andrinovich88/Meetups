import os

import pytest
from httpx import AsyncClient
from starlette.status import (HTTP_200_OK, HTTP_201_CREATED,
                              HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED,
                              HTTP_422_UNPROCESSABLE_ENTITY)


@pytest.mark.integration
async def test_sign_up_wo_field(client: AsyncClient):
    """
    Negative case w/o required field for sign_up API endpoint
    """
    test_payload = {
        "username": "string",
        "password": "string",
        "last_name": "string",
        "first_name": "string"
    }
    response = await client.post("/users/sign_up/", json=test_payload)
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == "field required"


@pytest.mark.integration
async def test_sign_up_incorrect_password(client: AsyncClient):
    """
    Negative test case with incorrect password for sign_up API endpoint
    """
    test_payload = {
        "username": "string",
        "password": "string",
        "last_name": "string",
        "first_name": "string",
        "email": "user@example.com"
    }
    response = await client.post("/users/sign_up/", json=test_payload)
    expected_message = 'password is too short, password needs at least one ' \
                       'upper case character, password needs at least one ' \
                       'special character, password needs at least one number'

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail']['message'] == expected_message


@pytest.mark.integration
async def test_sign_up_same_users(
        client: AsyncClient, mock_verification_email
):
    """
    Test case to check the possibility of creating two identical users
    """
    test_payload = {
        "username": "string",
        "last_name": "string",
        "first_name": "string",
        "email": "user@example.com",
        "password": "Yourstrongpassword123%"
    }
    user_a = await client.post("/users/sign_up/", json=test_payload)
    assert user_a.status_code == HTTP_201_CREATED

    user_b = await client.post("/users/sign_up/", json=test_payload)
    expected_message = {'detail': {'success': False,
                                   'message': 'User already registered'}}

    assert user_b.status_code == HTTP_400_BAD_REQUEST
    assert user_b.json() == expected_message


@pytest.mark.integration
async def test_sign_up_same_emails(
        client: AsyncClient, mock_verification_email
):
    """
    Test case to check the possibility of creating users with the same email
    """
    payload_a = {
        "username": "test_user_a",
        "last_name": "user_a",
        "first_name": "User_a",
        "email": "user2@example.com",
        "password": "Yourstrongpassword123%"
    }
    payload_b = {
        "username": "test_user_b",
        "last_name": "user_b",
        "first_name": "User_b",
        "email": "user2@example.com",
        "password": "Yourstrongpassword123%"
    }
    user_a = await client.post("/users/sign_up/", json=payload_a)
    assert user_a.status_code == HTTP_201_CREATED

    user_b = await client.post("/users/sign_up/", json=payload_b)
    expected_message = {'detail': {'success': False,
                                   'message': 'Email already registered'}}
    assert user_b.status_code == HTTP_400_BAD_REQUEST
    assert user_b.json() == expected_message


@pytest.mark.integration
async def test_sign_up_same_usernames(
        client: AsyncClient, mock_verification_email
):
    """
    Test case to check the possibility of creating users with the same username
    """
    payload_a = {
        "username": "test_user_c",
        "last_name": "user_a",
        "first_name": "User_a",
        "email": "user_c@example.com",
        "password": "Yourstrongpassword123%"
    }
    payload_b = {
        "username": "test_user_c",
        "last_name": "user_b",
        "first_name": "User_b",
        "email": "user_d@example.com",
        "password": "Yourstrongpassword123%"
    }
    user_a = await client.post("/users/sign_up/", json=payload_a)
    assert user_a.status_code == HTTP_201_CREATED

    user_b = await client.post("/users/sign_up/", json=payload_b)
    expected_message = {'detail': {'success': False,
                                   'message': 'Username already registered'}}
    assert user_b.status_code == HTTP_400_BAD_REQUEST
    assert user_b.json() == expected_message


@pytest.mark.integration
async def test_sign_up_possitive(
        client: AsyncClient, mock_verification_email
):
    """
    Positive test case for sign_up API endpoint
    """
    test_payload = {
        "username": "test_user_e",
        "last_name": "string",
        "first_name": "string",
        "email": "user_e@example.com",
        "password": "Yourstrongpassword123%"
    }

    response = await client.post("/users/sign_up/", json=test_payload)

    expected_message = {
        'success': True,
        'message': 'Verification mail has been sent (user_id=5)'
    }

    assert response.status_code == HTTP_201_CREATED
    assert response.json() == expected_message


@pytest.mark.integration
async def test_sign_in_positive(client: AsyncClient):
    """
    Positive test case for user authorization
    """
    username = os.getenv('FASTAPI_SUPERUSER_NAME')
    password = os.getenv('FASTAPI_SUPERUSER_PASS')

    headers = {'accept': 'application/json',
               'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'username': username, 'password': password}

    response = await client.post(
        "/users/sign_in/", data=payload, headers=headers
    )

    assert response.status_code == HTTP_200_OK


@pytest.mark.integration
async def test_sign_in_negative_wo_data(client: AsyncClient):
    """
    Negative test case for user authorization without form data
    """
    response = await client.post("/users/sign_in/")

    expected_response = {'detail': [

        {'loc': ['body', 'username'], 'msg': 'field required',
         'type': 'value_error.missing'},

        {'loc': ['body', 'password'], 'msg': 'field required',
         'type': 'value_error.missing'}

    ]}

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == expected_response


@pytest.mark.integration
async def test_sign_in_negative_incorrect_username(client: AsyncClient):
    """
    Negative test case for user authorization with incorrect username
    """
    username = 'test_username'
    password = os.getenv('FASTAPI_SUPERUSER_PASS')

    headers = {'accept': 'application/json',
               'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'username': username, 'password': password}

    response = await client.post(
        "/users/sign_in/", data=payload, headers=headers
    )
    expected_response = {'detail': {'success': False,
                                    'message': 'Incorrect email or password'}}

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == expected_response


@pytest.mark.integration
async def test_sign_in_negative_incorrect_password(client: AsyncClient):
    """
    Negative test case for user authorization with incorrect password
    """
    username = os.getenv('FASTAPI_SUPERUSER_NAME')
    password = 'test_password'

    headers = {'accept': 'application/json',
               'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'username': username, 'password': password}

    response = await client.post(
        "/users/sign_in/", data=payload, headers=headers
    )

    expected_response = {'detail': {'success': False,
                                    'message': 'Incorrect email or password'}}

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == expected_response


@pytest.mark.integration
async def test_get_user_profile_positive(
        client: AsyncClient, auth_user_headers: dict
):
    """
    Positive test case for getting user profile
    """
    response = await client.get("/users/profile/", headers=auth_user_headers)
    assert response.status_code == HTTP_200_OK


@pytest.mark.integration
async def test_get_user_profile_negative(
        client: AsyncClient, auth_user_headers: dict
):
    """
    Negative test case for getting user profile
    """
    auth_user_headers['Authorization'] = 'some_incorrect_token'
    response = await client.get("/users/profile/", headers=auth_user_headers)
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.integration
async def test_edit_user_profile_positive(
        client: AsyncClient, auth_user_headers: dict, mock_verification_email
):
    """
    Positive test case for testing 'edit_profile' endpoint
    """
    payload = {
        "last_name": "admin_test_last_name",
        "first_name": "admin_test_first_name"
    }

    response = await client.put(
        "/users/edit_profile/", json=payload, headers=auth_user_headers
    )

    expected_response = {'success': True,
                         'message': "User 'admin' has been updated"}

    assert response.status_code == HTTP_200_OK
    assert response.json() == expected_response


@pytest.mark.integration
async def test_edit_user_profile_wo_payload(
        client: AsyncClient, auth_user_headers: dict, mock_verification_email
):
    """
    Negative test case for testing 'edit_profile' endpoint without data
    """
    response = await client.put(
        "/users/edit_profile/", json={}, headers=auth_user_headers
    )
    expected_response = {
        'detail': {'success': False, 'message': 'No data to update'}
    }

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == expected_response


@pytest.mark.integration
async def test_edit_user_profile_email_registered(
        client: AsyncClient, auth_user_headers: dict, mock_verification_email
):
    """
    Negative test case for testing 'edit_profile' endpoint with registered
    email
    """
    payload = {
        "email": os.getenv('FASTAPI_SUPERUSER_EMAIL')
    }
    response = await client.put(
        "/users/edit_profile/", json=payload, headers=auth_user_headers
    )
    expected_response = {
        'detail': {'success': False, 'message': 'Email already registered'}
    }

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == expected_response


@pytest.mark.integration
async def test_edit_user_profile_short_password(
        client: AsyncClient, auth_user_headers: dict, mock_verification_email
):
    """
    Negative test case for user profile editor endpoint with incorrect password
    """
    payload = {"password": "short"}
    response = await client.put(
        "/users/edit_profile/", json=payload, headers=auth_user_headers
    )

    expected_response = {'detail': {
        'success': False,
        'message': 'password is too short, password needs at least one upper '
                   'case character, password needs at least one special '
                   'character, password needs at least one number'
    }}

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == expected_response


@pytest.mark.integration
async def test_delete_user_profile_positive(
        client: AsyncClient, auth_user_headers: dict
):
    """
    Positive test case for user profile removal
    """
    response = await client.delete(
        "/users/delete_user/", headers=auth_user_headers
    )
    expected_response = {'success': True,
                         'Message': 'User (user_id=1 has been deleted)'}

    assert response.status_code == HTTP_200_OK
    assert response.json() == expected_response


@pytest.mark.integration
async def test_upload_avatar_image_positive(
        client: AsyncClient, auth_user_headers: dict, test_image: dict,
        mock_files_saving
):
    """
    Positive test case for user avatar uploading
    """
    auth_user_headers['content-type'] = 'multipart/form-data;boundary=' \
                                        '***some_boundary***'

    response = await client.post(
        url="/users/upload_avatar",
        headers=auth_user_headers,
        files=test_image
    )

    expected_response = {
        'success': True,
        'message': 'User avatar upload successful (user_id = 1)'
    }

    assert response.status_code == HTTP_201_CREATED
    assert response.json() == expected_response


@pytest.mark.integration
async def test_upload_avatar_image_incorrect_content(
        client: AsyncClient, auth_user_headers: dict, mock_files_saving
):
    """
    Negative test case for user avatar uploading with incorrect content
    """
    auth_user_headers['content-type'] = 'multipart/form-data;boundary=' \
                                        '***some_boundary***'

    files = {"avatar_image": b'Hello world'}

    response = await client.post(
        url="/users/upload_avatar",
        headers=auth_user_headers,
        files=files
    )

    expected_response = {
        'detail': {'success': False, 'message': 'Incorrect file type'}
    }

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == expected_response
