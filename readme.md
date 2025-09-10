# Odyssey

Starlette-based web application for displaying geographical locations on an interactive map.

Contains simple user authentication and location management features with a SQLite database backend.


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