# Odyssey

This is a work-in-progress interactive travel photography / blogging website. Built with starlette, jinja2 and sqlite3.


## Development

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```
2. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # unix / osx
   venv\Scripts\activate     # windows
   ```
3. Install the required packages:
   ```bash
   pip3 install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with copied contents from `.env.example` and set your own secret key.
5. Run the application:
   ```bash
   python3 main.py

   # or directly with uvicorn
   uvicorn main:app --reload
   ```
6. In a separate terminal, run the database seed script to set up the initial SQLite database:
   ```bash
   python3 scripts/seed.py
   ```
7. Open your web browser and navigate to `http://127.0.0.1:8000/register` to create a new admin account.


## Quick Demo

https://github.com/user-attachments/assets/60215e27-aa76-4069-bb0d-18bfbb5c1fb9


## Planned Features

- [x] Map integration (leaflet & openstreetmap)
- [x] User authentication
- [ ] Admin panel
  - [ ] UI
  - [ ] CRUD
    - [x] Create a new location
    - [x] View a list of all locations
    - [ ] Edit a location
    - [x] Delete a location by its `id`
    - [x] Config: functional `allow_registration` toggle
  - [ ] Blog CMS
  - [ ] Gallery CMS
- [ ] Gallery integration
- [ ] Blog integration
