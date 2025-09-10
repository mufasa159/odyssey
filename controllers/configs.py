from controllers.database import get_db_connection
from starlette.requests import Request
from starlette.responses import JSONResponse
from controllers.auth import require_auth


async def get_all_configs() -> dict:
    conn = get_db_connection()
    configs = conn.execute('SELECT * FROM configs').fetchall()
    conn.close()

    response = {}

    for config in configs:
        if config['value'] in {'true', 'false'}:
            response[config['key']] = True if config['value'] == 'true' else False
        else:
            response[config['key']] = config['value']

    return response


@require_auth()
async def toggle_allow_registration(request: Request):
    data = await request.json()
    allow = data.get('allow', False)

    try:
        conn = get_db_connection()
        conn.execute('UPDATE configs SET value = ? WHERE key = "allow_registration"', ('true' if allow else 'false',))
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error updating 'allow_registration': {e}")

    return JSONResponse({
        'status': 'success',
        'allow_registration': allow
    })
