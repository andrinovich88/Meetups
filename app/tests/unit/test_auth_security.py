import os

import pytest
from auth.utils.security import (check_strong_password, decode_jwt_token,
                                 encode_jwt_token, hash_password,
                                 validate_password)
from jose import jwt
from werkzeug.security import check_password_hash, generate_password_hash


@pytest.mark.unit
def test_validate_password():
    password = 'test_password'

    password_hash_a = 'test_hash_password'
    password_hash_b = generate_password_hash(password)

    response_a = validate_password(password, password_hash_a)
    response_b = validate_password(password, password_hash_b)

    assert response_a is False
    assert response_b is True


@pytest.mark.unit
def test_hash_password():
    password = 'test'

    test_hash = generate_password_hash(password)
    response = hash_password(password)
    is_same = check_password_hash(response, password)

    assert is_same
    assert test_hash != response


@pytest.mark.unit
def test_check_strong_password():
    password_a = 'short'
    password_b = 'verylongpassword'
    password_c = 'VeryLongPasswordCamel'
    password_d = 'VeryLongPasswordCamelDigit1'
    password_e = 'VeryLongPasswordCamelDigit1Special%'

    expected_response_a = "password is too short, " \
                          "password needs at least one upper case character, "\
                          "password needs at least one special character, " \
                          "password needs at least one number"

    expected_response_b = "password needs at least one upper case character," \
                          " password needs at least one special character," \
                          " password needs at least one number"

    expected_response_c = "password needs at least one special character, " \
                          "password needs at least one number"

    expected_response_d = "password needs at least one special character"

    response_a = check_strong_password(password_a)
    response_b = check_strong_password(password_b)
    response_c = check_strong_password(password_c)
    response_d = check_strong_password(password_d)
    response_e = check_strong_password(password_e)

    assert response_e == ''
    assert response_a == expected_response_a
    assert response_b == expected_response_b
    assert response_c == expected_response_c
    assert response_d == expected_response_d


@pytest.mark.unit
def test_encode_jwt_token():
    crypto_string = 'test_token'

    response_a = encode_jwt_token(crypto_string)
    response_b = encode_jwt_token(crypto_string)

    key = os.getenv('SECRET_KEY')
    response_string = jwt.decode(response_a, key, algorithms="HS256")['data']

    assert response_a == response_b
    assert response_string == crypto_string


@pytest.mark.unit
def test_decode_jwt_token():
    crypto_string = 'test_token'

    token = encode_jwt_token(crypto_string)

    response_a = decode_jwt_token(token)
    response_b = decode_jwt_token(token)

    assert response_a == crypto_string == response_b
