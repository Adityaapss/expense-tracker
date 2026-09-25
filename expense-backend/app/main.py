from fastapi import FastAPI

from app.routers import auth, budgets, categories, expenses, reports

app = FastAPI(title="Expense Tracker API")

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)
app.include_router(budgets.router)
app.include_router(reports.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
