from fastapi import FastAPI

from app.routers import auth

app = FastAPI(title="Expense Tracker API")

app.include_router(auth.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
