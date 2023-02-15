from auth.utils.security import encode_jwt_token
from config.settings import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM_NAME=settings.MAIL_ADMIN,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM=settings.MAIL_ADMIN,
    MAIL_PORT=settings.MAIL_PORT,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    MAIL_SSL_TLS=False,
    MAIL_STARTTLS=True,
)


def generate_html_message(username: str, base_url: str) -> str:
    """
    Function for HTML verification mail content generation
    :param username: User nickname in string format
    :param base_url: Parent URL for composing a confirmation letter
    :return: HTML content in string format
    """
    token = encode_jwt_token(username)
    return f"""<p>Hi {username}, this is email address confirmation.
    To continue using the meetup service, follow the link:<br>
    "{base_url}users/activate_user/{token}"</br>.
    <br>Thanks for using Meetups</br></p> """


async def send_verification_email(email: str, html: str) -> None:
    """
    Function for sending email
    :param email: target email address
    :param html: HTML message for sending
    """
    message = MessageSchema(
        subject="Registration confirmation",
        recipients=[email],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
