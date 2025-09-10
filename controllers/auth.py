import jwt, bcrypt, sqlite3, os
from dotenv import load_dotenv
from functools import wraps
from controllers.database import get_db_connection
from models.user import User
from datetime import datetime, timedelta, timezone
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials
)

load_dotenv('./.env')

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

templates = Jinja2Templates(directory='templates')


async def login(request: Request):
    data = await request.form()
    username = str(data.get('username'))
    password = str(data.get('password'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": username,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + access_token_expires
        }
        access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        # return token as cookie
        return RedirectResponse(
            url='/admin',
            status_code=302,
            headers={
                "Set-Cookie": f"token={access_token}; HttpOnly; Path=/; Max-Age={ACCESS_TOKEN_EXPIRE_MINUTES * 60}; SameSite=Lax; Secure;"
            }
        )

    else:
        return RedirectResponse(url='/login?e=login_failed', status_code=302)


async def register(request: Request):
    data = await request.form()
    name = str(data.get('name'))
    username = str(data.get('username'))
    password = str(data.get('password'))

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_connection()

    try:
        # check if registration is allowed
        allow_registration = conn.execute('SELECT value FROM configs WHERE key = ?', ('allow_registration',)).fetchone()
        if allow_registration is None or allow_registration['value'].lower() != 'true':
            conn.close()
            return RedirectResponse(url='/register?e=signup_disabled', status_code=302)

        # register user
        conn.execute('INSERT INTO users (name, username, password) VALUES (?, ?, ?)', (name, username, hashed_password))
        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return RedirectResponse(url='/register?e=username_exists', status_code=302)

    conn.close()
    return RedirectResponse(url='/login?s=signup_success', status_code=302)


def logout(request: Request):
    response = RedirectResponse(url='/', status_code=302)
    response.delete_cookie('token', path='/')
    return response


def verify_token(token: str) -> tuple[str, str] | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user is None:
            return None

        return username, user['name']

    except jwt.PyJWTError:
        return None


class JWTAuthenticationBackend(AuthenticationBackend):
    async def authenticate(self, request: Request):
        token = request.cookies.get("token")

        if not token:
            return

        user = verify_token(token)

        if user is None:
            return

        username, name = user

        return AuthCredentials(["authenticated"]), User(username, name)


def require_auth(redirect_url="/login", message_key="unauthorized"):
    """
    Custom decorator that redirects unauthenticated users to login page
    instead of returning 403 Forbidden

    Usage:
        @require_auth()
        async def protected_route(request: Request):
            return templates.TemplateResponse(request, 'template.html')

        @require_auth(redirect_url="/custom-login", message_key="custom_error")
        async def custom_protected_route(request: Request):
            return templates.TemplateResponse(request, 'template.html')

    Args:
        redirect_url (str): URL to redirect to when user is not authenticated
        message_key (str): Key to use for error message (from models.messages)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request):
            if not request.user.is_authenticated:
                redirect_with_message = f"{redirect_url}?e={message_key}"
                return RedirectResponse(url=redirect_with_message, status_code=302)
            return await func(request)
        return wrapper
    return decorator


def require_no_auth(redirect_url="/admin"):
    """
    Custom decorator that redirects authenticated users away from certain pages
    (like login or register) to prevent them from accessing those pages again.

    Usage:
        @require_no_auth()
        async def login_page(request: Request):
            return templates.TemplateResponse(request, 'login.html')

    Args:
        redirect_url (str): URL to redirect to when user is authenticated
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request):
            if request.user.is_authenticated:
                redirect_with_message = f"{redirect_url}"
                return RedirectResponse(url=redirect_with_message, status_code=302)
            return await func(request)
        return wrapper
    return decorator
