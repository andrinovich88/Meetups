import re
from datetime import datetime, timedelta

from config.settings import settings
from jose import jwt
from werkzeug.security import check_password_hash, generate_password_hash


def validate_password(password: str, hashed_password: str) -> bool:
    """
    Function for matching hashed and unhashed passwords
    :param password: unhashed password in string format
    :param hashed_password: password hash on string format
    :return: boolean statement
    """
    return check_password_hash(hashed_password, password)


def hash_password(password: str) -> str:
    """
    Function for hashing passwords
    :param password: password in string format
    :return: hashed password
    """
    return generate_password_hash(password)


def check_strong_password(password: str) -> str | None:
    """
    Function for checking new password content
    :param password: unhashed password in string format
    :return: NoneType or string with broken password rule
    """
    rules = [
        ('password is too short', r'.{8}'),
        ('password needs at least one lower case character', r'[a-z]'),
        ('password needs at least one upper case character', r'[A-Z]'),
        ('password needs at least one special character', r'[-_?!@#$%^&*]'),
        ('password needs at least one number', r'[0-9]'),
    ]

    err_msg = ', '.join(
        req
        for req, regex in rules
        if not re.search(regex, password)
    )
    return err_msg


def encode_jwt_token(crypto_string: str) -> str:
    """
    Function for token generation based on passed string
    :param crypto_string: line to encrypt
    :return: encrypted token in string format
    """
    key = settings.SECRET_KEY
    data = {"data": crypto_string, "exp": datetime.utcnow()}
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, key, algorithm="HS256")


def decode_jwt_token(token: str) -> str:
    """
    Function for token decryption
    :param token: encrypted string
    :return: decrypted string
    """
    key = settings.SECRET_KEY
    data_dict = jwt.decode(token, key, algorithms="HS256")
    return data_dict.get('data')
