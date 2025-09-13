import json, httpx, ssl, certifi
from datetime import datetime
from controllers.database import get_db_connection
from starlette.requests import Request
from starlette.responses import JSONResponse
from controllers.auth import require_auth


ssl_context = ssl.create_default_context(cafile=certifi.where())


def get_all_locations(request: Request):
    conn = get_db_connection()
    q = 'SELECT * FROM locations l LEFT JOIN locations_boundaries lb ON l.id = lb.location_id ORDER BY l.created_at DESC'
    locations = conn.execute(q).fetchall()
    conn.close()

    res: list[dict] = []

    for location in locations:
        if location['metadata']:
            location = dict(location)
            location['metadata'] = json.loads(location['metadata'])

        if location['boundary']:
            location = dict(location)
            location['boundary'] = json.loads(location['boundary'])

        res.append(dict(location))

    return JSONResponse(res)


async def get_all_locations_minimal_by_pages() -> dict[str, list]:
    conn = get_db_connection()
    q = 'SELECT id, name, created_at, updated_at FROM locations ORDER BY created_at DESC'
    locations = conn.execute(q).fetchall()
    conn.close()

    MAX_PER_PAGE = 4

    response: dict[str, list] = {"1": []}
    current_page: int = 1

    for location in locations:
        if location['created_at']:
            location = dict(location)
            location['created_at'] = datetime.fromisoformat(
                location['created_at']
            ).strftime('%b %d, %Y, %H:%M:%S')

        if location['updated_at']:
            location = dict(location)
            location['updated_at'] = datetime.fromisoformat(
                location['updated_at']
            ).strftime('%b %d, %Y, %H:%M:%S')

        response[str(current_page)].append(dict(location))

        if len(response[str(current_page)]) >= MAX_PER_PAGE:
            current_page += 1
            response[str(current_page)] = []

    return response


def get_location_by_id(request: Request):
    location_id = int(request.path_params.get('location_id', 0))

    conn = get_db_connection()
    q = 'SELECT * FROM locations WHERE id = ?'
    location = conn.execute(q, (location_id,)).fetchone()
    conn.close()

    return JSONResponse(dict(location)) if location else JSONResponse(
        status_code=404,
        content={'error': 'Location not found'}
    )


@require_auth()
async def add_location(request: Request):
    data = await request.json()

    name = str(data.get('name')).strip()
    description = str(data.get('description')).strip()
    latitude = float(data.get('latitude')) if data.get('latitude') else None
    longitude = float(data.get('longitude')) if data.get('longitude') else None
    metadata = data.get('metadata', {})

    if not all([name, description]):
        return JSONResponse(
            status_code=400,
            content={'error': 'Missing required fields'}
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO locations (name, description, latitude, longitude, metadata) VALUES (?, ?, ?, ?, ?)',
        (
            name,
            description,
            latitude,
            longitude,
            json.dumps(metadata) if metadata else None
        )
    )
    conn.commit()

    if not longitude or not latitude:
        try:
            async with httpx.AsyncClient(verify=ssl_context) as client:

                # fetch location boundary data from openstreetmap
                # useful info: https://operations.osmfoundation.org/policies/nominatim/
                response = await client.get(
                    'https://nominatim.openstreetmap.org/search',
                    params={
                        'q': name,
                        'format': 'json',
                        'polygon_geojson': 1,
                        'limit': 1
                    },
                    timeout=10.0,
                    headers={'User-Agent': 'Odyssey/1.0 (https://github.com/mufasa159/odyssey)'}
                )
                response.raise_for_status()
                results = response.json()

                if results and isinstance(results, list):
                    result = dict(results[0])

                    # for type consistency
                    temp_lat = result.get('lat')
                    temp_lon = result.get('lon')

                    if temp_lat:
                        latitude = float(temp_lat)

                    if temp_lon:
                        longitude = float(temp_lon)

                    # insert location boundary
                    q = "INSERT INTO locations_boundaries (location_id, boundary) VALUES (?, ?)"
                    cursor.execute(q, (cursor.lastrowid, json.dumps(result)))

                    # update location with fetched lat/lon
                    if latitude and longitude:
                        cursor.execute(
                            'UPDATE locations SET latitude = ?, longitude = ? WHERE id = ?',
                            (latitude, longitude, cursor.lastrowid)
                        )

                    conn.commit()

        except Exception as e:
            print(f"Error fetching geolocation data: {e}")

    location_id = cursor.lastrowid
    conn.close()

    return JSONResponse(
        status_code=201,
        content={
            'message': 'Location added',
            'location_id': location_id
        }
    )


@require_auth()
async def edit_location(request: Request):
    location_id = request.path_params.get('location_id')

    if location_id:
        location_id = int(location_id)

    else:
        return JSONResponse(
            status_code=400,
            content={'error': 'Location ID is required'}
        )

    data = await request.json()

    name = str(data.get('name')).strip()
    description = str(data.get('description')).strip()
    latitude = float(data.get('latitude')) if data.get('latitude') else None
    longitude = float(data.get('longitude')) if data.get('longitude') else None
    metadata = data.get('metadata', {})

    if not all([name, description]):
        return JSONResponse(
            status_code=400,
            content={'error': 'Missing required fields'}
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE locations SET name = ?, description = ?, latitude = ?, longitude = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (
            name,
            description,
            latitude,
            longitude,
            json.dumps(metadata) if metadata else None,
            location_id
        )
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    if rows_affected == 0:
        return JSONResponse(
            status_code=404,
            content={'error': 'Location not found'}
        )

    return JSONResponse(
        status_code=200,
        content={'message': 'Location updated'}
    )


@require_auth()
async def delete_location(request: Request):
    location_id = request.path_params.get('location_id')

    if location_id:
        location_id = int(location_id)

    else:
        return JSONResponse(
            status_code=400,
            content={'error': 'Location ID is required'}
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM locations WHERE id = ?', (location_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    if rows_affected == 0:
        return JSONResponse(
            status_code=404,
            content={'error': 'Location not found'}
        )

    return JSONResponse(
        status_code=200,
        content={'message': 'Location deleted'}
    )
