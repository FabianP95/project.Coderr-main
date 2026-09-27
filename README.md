# Coderr

Coderr is a Django-based backend project for a freelancer-developer platform. The repository includes a frontend prototype in the `frontend/` directory and a Django backend setup that is intended to connect to it.

## Project goal

The project is designed to power a platform where:

- freelancers can present themselves and their services
- customers can search and request offers
- users can register, log in, and manage profiles
- offers, orders, and reviews can be created and displayed

This is a training project for backend development with Django and Django REST Framework.

## Tech stack

- Python
- Django
- Django REST Framework
- SQLite (default development database)
- Vanilla JavaScript frontend in `frontend/`

## Repository structure

- `core/` – Django project configuration
- `frontend/` – static frontend prototype and templates
- `manage.py` – Django management entry point
- `requirements.txt` – Python dependencies
- `db.sqlite3` – local SQLite database file

## Requirements

Make sure the following are installed:

- Python 3.x
- pip
- virtual environment support

## Local setup

1. Open a terminal in the project root.
2. Activate the virtual environment:

   Windows PowerShell:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   or if you are using a standard venv:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Open the app in the browser at:
   ```text
   http://127.0.0.1:8000/
   ```

## Frontend

The static frontend is located in the `frontend/` folder. It is a prototype that can be opened locally in a browser, and it is meant to be connected to the Django backend once the API and models are implemented.

## Notes

- Code comments and variable names should be written in English.
- This project is a learning project and is intended for educational use.
- The frontend and backend are meant to be connected as part of the course work.
