import uvicorn
from controllers.database import get_db_connection
from controllers.configs import (
    get_all_configs,
    toggle_allow_registration
)
from controllers.locations import (
    get_all_locations,
    get_all_locations_minimal_by_pages,
    add_location,
    delete_location,
)
from controllers.auth import (
    require_auth,
    require_no_auth,
    login,
    register,
    logout
)
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.middleware.authentication import AuthenticationMiddleware
from controllers.auth import JWTAuthenticationBackend
from models.messages import message

templates = Jinja2Templates(directory='templates')

templates.env.globals.update({
    'navigation': templates.get_template('macros/navigation.html').module.navigation
})


async def homepage(request: Request):
    return templates.TemplateResponse(request, 'index.html', {
        'logged_in': request.user.is_authenticated,
    })


async def handle_message(request: Request):
    s = request.query_params.get('s')
    e = request.query_params.get('e')

    context = {}

    if e:
        context['error'] = message.get(e)

    if s:
        context['success'] = message.get(s)

    return context


@require_no_auth()
async def login_page(request: Request):
    context = await handle_message(request)
    return templates.TemplateResponse(request, 'login.html', context)


@require_no_auth()
async def register_page(request: Request):
    cursor = get_db_connection().cursor()
    cursor.execute('SELECT value FROM configs WHERE key = ?', ('allow_registration',))
    allow_registration = cursor.fetchone()
    cursor.close()

    context = await handle_message(request)
    context['allow_registration'] = allow_registration and allow_registration[0] == 'true'
    return templates.TemplateResponse(request, 'register.html', context)


@require_auth()
async def admin_page(request: Request):
    locations = await get_all_locations_minimal_by_pages()
    configs = await get_all_configs()

    context = await handle_message(request)

    total_locations = 0
    for _ in locations.values():
        total_locations += len(_)

    context['location_count'] = total_locations
    context['locations'] = locations

    if request.user.display_fullname:
        context['user_fullname'] = str(request.user.display_fullname).strip()

    return templates.TemplateResponse(request, 'admin.html', {**context, **configs})


app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Mount('/static', StaticFiles(directory='static'), name='static'),

    Route('/locations', get_all_locations, methods=['GET']),
    Route('/locations/create', add_location, methods=['POST']),
    Route('/locations/delete/{location_id:int}', delete_location, methods=['DELETE']),

    Route('/config/allow-registration', toggle_allow_registration, methods=['POST']),

    Route('/login', login_page, methods=['GET']),
    Route('/login', login, methods=['POST']),
    Route('/register', register_page, methods=['GET']),
    Route('/register', register, methods=['POST']),
    Route('/logout', logout, methods=['GET']),

    Route('/admin', admin_page, methods=['GET']),
])

app.add_middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend())


@app.on_event("startup")
async def startup_event():
    conn = get_db_connection()
    with open('database/schema.sql') as f:
        conn.executescript(f.read())
    conn.close()


if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host='127.0.0.1',
        port=8000,
        reload=True
    )
