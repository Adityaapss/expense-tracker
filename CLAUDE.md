# Expense Tracker – Project Guide

This file describes the whole project. Read it before making any changes.

## 1. What we are building

An expense tracker app for Indian users. Users record their spending, see where
their money goes (by category), set budgets, share expenses with friends, and
later get their UPI payments added automatically plus AI-powered insights.

The goal is to build a high-quality app that many people will use, so code
should be clean, secure, and easy to extend.

**One backend serves two clients:**
- Android app (Kotlin) – main client
- Web app (React) – second client

Both clients talk to the backend only through a REST API with JSON.

## 2. About the developer (important)

I am new to backend and app development. Please:
- Explain each step in simple English before doing it
- Build in small steps, and make sure each step runs before moving on
- Tell me what each new file does and why it is needed
- Ask me before big decisions (new libraries, changing the structure)
- When something fails, explain the error and the fix

## 3. Tech stack

| Part | Choice |
|---|---|
| Backend framework | FastAPI (Python 3.11+) |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 (typed `Mapped` / `mapped_column` style) |
| Migrations | Alembic |
| Validation | Pydantic v2 + pydantic-settings |
| Auth | JWT (pyjwt) + bcrypt password hashing |
| Server | Uvicorn |
| Android client | Kotlin + Retrofit/OkHttp |
| Web client | React |
| Hosting (later) | Render / Railway / VPS, database on Neon or Supabase |

Operating system: macOS, VS Code.

## 4. Project structure

```
Desktop/expense-tracker/
├── expense-backend/      <- this project (FastAPI)
├── android-app/          <- later
└── web-app/              <- later
```

Backend layout:

```
expense-backend/
├── app/
│   ├── main.py           FastAPI app, includes all routers
│   ├── config.py         settings from .env (DATABASE_URL, SECRET_KEY)
│   ├── database.py       engine, SessionLocal, Base, get_db()
│   ├── models/           SQLAlchemy models (database tables)
│   ├── schemas/          Pydantic models (request/response shapes)
│   ├── routers/          API endpoints, one file per feature
│   ├── services/         business logic (keep routers thin)
│   └── core/             security (hashing, JWT), dependencies
├── alembic/              database migrations
├── .env                  secrets (never commit)
├── .env.example
├── requirements.txt
└── README.md
```

## 5. Coding rules

- All API routes start with `/api/` (e.g. `/api/expenses`)
- Money is always `Numeric(10, 2)` in the database and `Decimal` in Python, never float
- Every expense, budget, and category query must filter by the logged-in user
  (a user must never see another user's data)
- Never return `password_hash` in any response
- Routers handle HTTP only; logic goes in `services/`
- Use Alembic for every database change (no manual SQL table changes)
- Keep secrets in `.env` only
- Dates in API: ISO format (`2026-09-25`); months as `"YYYY-MM"`
- Return clear error messages with correct HTTP status codes (400, 401, 403, 404)

## 6. Database models

Already created in `app/models/models.py`:

**User** – id, name, email (unique), password_hash, created_at

**Category** – id, name, icon, user_id
- `user_id = NULL` means a default category for everyone
- Default categories: Food, Education, Entertainment, Travel, Bills,
  Shopping, Health, Groceries, Rent, Other
- Users can also create their own categories

**Expense** – id, user_id, category_id, amount, expense_date, merchant, note,
payment_method (cash / upi / card), source (manual / sms / notification / statement),
created_at
- `merchant` and `source` exist already so Version 2 (auto-detection) needs no big changes

**Budget** – id, user_id, category_id, month ("2026-09"), amount
- Unique per (user, category, month)

Planned later: Group, GroupMember, Split (shared expenses), RecurringExpense,
MerchantCategoryRule (for learned auto-categorization).

## 7. API endpoints (planned)

Auth
- `POST /api/auth/register`
- `POST /api/auth/login` → returns JWT access token
- `GET  /api/auth/me`

Categories
- `GET    /api/categories` (default + user's own)
- `POST   /api/categories`
- `DELETE /api/categories/{id}` (own categories only)

Expenses
- `GET    /api/expenses?month=2026-09&category_id=&page=`
- `POST   /api/expenses`
- `PUT    /api/expenses/{id}`
- `DELETE /api/expenses/{id}`

Budgets
- `GET  /api/budgets?month=2026-09` (with amount spent and % used)
- `POST /api/budgets`

Reports
- `GET /api/reports/monthly?month=2026-09` (total, by category)
- `GET /api/reports/trend?months=6` (month-by-month totals)

Imports (Version 2)
- `POST /api/imports/sms` (Android sends parsed transaction data)
- `POST /api/imports/statement` (PDF/CSV upload)

Groups & splits (Version 2)
- `POST /api/groups`, `GET /api/groups`, `POST /api/groups/{id}/expenses`,
  `GET /api/groups/{id}/balances`

## 8. Features and roadmap

### Version 1 – Core app (current focus)
1. Project setup, database, Alembic ✅
2. Register / login with JWT ✅
3. Categories (default + custom) ✅
4. Expenses: add, edit, delete, list, filter by month and category ✅
5. Budgets per category per month, warnings at 80% and 100% ✅
6. Reports: total per month, spending by category (pie chart data),
   month-to-month trend (bar chart data) ✅
7. Connect the Kotlin Android app  <- CURRENT STEP

Shared expenses (groups, who paid, who owes whom) was originally planned for
Version 1 but has been moved to Version 2 - see below.

### Version 2 – Automatic UPI detection + shared expenses
- Android app reads bank SMS ("Rs.250 debited via UPI to Swiggy") and payment
  app notifications (PhonePe, Paytm, GPay), extracts amount + merchant,
  sends to backend
- Bank statement import (PDF/CSV) parsed on the backend (pdfplumber, pandas)
- Auto-categorization (Swiggy → Food, Uber → Travel), learns from user corrections
- Duplicate detection (same payment from SMS and notification counted once)
- Note: SMS reading on Android happens in the app, not the backend. Google Play
  restricts SMS permission, so all three methods are kept as fallbacks.
- Shared expenses: groups, who paid, who owes whom (moved from Version 1)

### Version 3 – Sharing extras and smart features
- Recurring expenses (rent, subscriptions, EMIs)
- Export reports to PDF / Excel
- Offline mode in Android app with sync

## 9. AI features (ideas, not final yet)

The backend will call an AI API from Python. No custom model training needed.
Candidates:
- Smart auto-categorization of unknown merchants
- Monthly AI spending summary
- Chat with your expenses ("How much did I spend on food last month?")
- Receipt / bill photo scanning
- Voice entry, including Hindi / Hinglish
- Smarter SMS and statement parsing for any bank format
- Spending predictions and budget warnings before overspending
- Saving tips, unusual spending alerts, budget suggestions, savings goal coach

Rules for AI features:
- Cache results (once "Swiggy → Food" is known, don't call the AI again)
- Send only needed data (merchant, amount), never name, email, or phone
- Keep AI code in its own service so the provider can be changed later

## 10. Security and privacy

- Passwords hashed with bcrypt
- JWT tokens with expiry
- Validate all input with Pydantic
- Users can only access their own data
- Financial data is private; be careful with logging (no amounts + user info in logs)

## 11. Local development notes

- Run server: `uvicorn app.main:app --reload`
- API docs: http://localhost:8000/docs
- Android emulator reaches the backend at `http://10.0.2.2:8000`
- Real phone: use the computer's local IP, e.g. `http://192.168.1.5:8000`
- Migrations: `alembic revision --autogenerate -m "message"` then `alembic upgrade head`

## 12. Current status

- Folder structure, config.py, database.py, main.py, and models are created
- venv created (Python 3.13, needed since macOS's built-in python3 is 3.9),
  requirements installed, .env created, Alembic set up, tables created in
  Postgres (expense_db)
- Auth built and tested: `POST /api/auth/register`, `POST /api/auth/login`,
  `GET /api/auth/me` (`core/security.py`, `core/deps.py`, `services/auth_service.py`,
  `schemas/user.py`)
- Categories built and tested: `GET/POST /api/categories`, `DELETE /api/categories/{id}`.
  Default categories (Food, Travel, etc.) are seeded via an Alembic data
  migration (`alembic/versions/e908047d0fb3_seed_default_categories.py`), not a
  manual script
- Expenses built and tested: `GET/POST /api/expenses`, `PUT/DELETE /api/expenses/{id}`,
  with month + category filtering and pagination
- Budgets built and tested: `GET/POST /api/budgets`. `POST` acts as create-or-update
  (upsert) per category+month since there's no separate `PUT /api/budgets/{id}`.
  Response includes computed `spent`, `percent_used`, and `status`
  (`ok` / `warning` at 80% / `over` at 100%)
- Reports built and tested: `GET /api/reports/monthly` (total + category
  breakdown), `GET /api/reports/trend` (month-by-month totals, zero-filled for
  months with no spending)
- `app/services/date_utils.py` holds the shared "YYYY-MM" → month date-range
  helper used by expenses, budgets, and reports
- Backend side of Version 1 core is functionally complete except connecting
  the Android app. Shared expenses (groups/splits) was moved out of Version 1
  into Version 2 - see section 8
- Next: connect the Kotlin Android app
