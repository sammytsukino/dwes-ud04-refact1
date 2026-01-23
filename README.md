Book Library (Django)
====================

A minimal Django app to manage a catalog of books. The goal of this exercise is to practice testing in Django: writing model and view tests, asserting validation rules, and tracking coverage.

Project structure
-----------------
- `bookproject/`: Django project configuration.
- `bookapp/`: Application with models, forms, views, URLs, and templates.
- `db.sqlite3`: Local SQLite database (dev only).

Requirements
------------
- Python 3.10+
- Django (see `requirements.txt`)
- SQLite (bundled with Python)

Setup
-----
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Apply migrations: `python manage.py migrate`.
4. (Optional) Load sample data or create books through the UI at `/`.

Running the app
---------------
- Start the dev server: `python manage.py runserver` (default at http://localhost:8000/).

Testing focus
-------------
- Run the full suite: `python manage.py test`.
- Generate coverage report (HTML):
	- `coverage run manage.py test`
	- `coverage html` (outputs to `htmlcov/index.html`).
- Targets for verification:
	- Model validation (e.g., required fields, positive page counts).
	- Form validation and error messages.
	- View behaviors: list/detail/create/update/delete flows, redirects, and templates.
	- URL routing matches expected view functions/classes.

Writing tests
-------------
- Place tests in `bookapp/tests.py` (or split into a `tests/` package if desired).
- Use Django’s `TestCase` for DB-backed tests; leverage `setUpTestData` to avoid per-test setup cost.
- Prefer descriptive test names and clear given/when/then comments when scenarios are complex.
- Mock external calls if added later; current app is self-contained.

Coverage goals
--------------
- Aim for high coverage of models, forms, and views; templates can be covered via view response assertions.
- After running `coverage html`, open `htmlcov/index.html` to inspect uncovered lines and add focused tests.

Common commands
---------------
- Format/inspect: `python manage.py check`
- Shell: `python manage.py shell`
- Reset local DB: delete `db.sqlite3` and rerun migrations.

Notes
-----
- The project is intentionally small to keep the focus on testing practices rather than features.
