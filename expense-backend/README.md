# Expense Tracker Backend (FastAPI)

## Setup
1. python3.13 -m venv venv  (needs Python 3.10+; macOS's built-in python3 is 3.9)
2. Activate: venv\Scripts\activate (Windows) or source venv/bin/activate (Mac/Linux)
3. pip install -r requirements.txt
4. Copy .env.example to .env and fill in your database user/password (keep the `postgresql+psycopg2://` prefix)
5. createdb expense_db
6. alembic upgrade head  (creates all tables)
7. uvicorn app.main:app --reload
8. Open http://localhost:8000/docs

## Changing models
After editing app/models, run:
- alembic revision --autogenerate -m "describe change"
- alembic upgrade head
