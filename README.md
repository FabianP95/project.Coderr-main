# Coderr

Coderr is the backend for a freelancer-developer platform, built with Django and Django REST Framework. The repository also contains the frontend in the `frontend/` directory, which consumes the REST API provided by the backend.

## Project goal

The platform allows:

- business users (freelancers) to present themselves and their services
- customers to search offers and place orders
- users to register, log in, and manage their profiles
- customers to review business users

This is a training project for backend development with Django and Django REST Framework.

## Tech stack

- Python 3.14
- Django
- Django REST Framework (token authentication)
- django-filter
- django-cors-headers
- python-dotenv
- SQLite (development database)
- Ruff (linting)

## Repository structure

- `core/` – Django project configuration (settings, root URLs)
- `user_auth_app/` – custom user model, registration, login, and profiles
- `offers_app/` – offers and offer details
- `orders_app/` – orders between customers and business users
- `reviews_app/` – reviews for business users
- `base_app/` – general platform information (statistics)
- `frontend/` – frontend that consumes the API
- `postman/` – Postman collections and environments for the API
- `requirements.txt` – Python dependencies
- `requirements-dev.txt` – development dependencies (includes Ruff)
- `.env.template` – template for the required environment variables

## Requirements

- Python 3.14
- pip
- venv

## Local setup

1. Clone the repository and open a terminal in the project root.

2. Create and activate a virtual environment:

   Windows PowerShell:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   macOS / Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   For development (includes Ruff):
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Create the `.env` file from the template and set a secret key:

   Windows PowerShell:
   ```powershell
   Copy-Item .env.template .env
   ```

   macOS / Linux:
   ```bash
   cp .env.template .env
   ```

   Then set `DJANGO_SECRET_KEY` in `.env` to any random string.

5. Create the migrations:

   Migration files are not part of the repository, so they have to be generated locally first:
   ```bash
   python manage.py makemigrations
   ```

6. Apply the migrations:
   ```bash
   python manage.py migrate
   ```

7. (Optional) Create an admin user:
   ```bash
   python manage.py createsuperuser
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```

   The API is available at `http://127.0.0.1:8000/api/`, the admin panel at `http://127.0.0.1:8000/admin/`.

## Tests and linting

Run the test suite:
```bash
python manage.py test
```

Run the linter:
```bash
ruff check .
```

Both are also executed automatically by the GitHub Actions workflow in `.github/workflows/ci.yml` on every push and pull request to `main`.


