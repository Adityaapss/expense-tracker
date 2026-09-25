from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

PaymentMethod = Literal["cash", "upi", "card"]


class ExpenseCreate(BaseModel):
    """Shape of the JSON body for POST /api/expenses."""

    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    expense_date: date
    category_id: int | None = None
    merchant: str | None = Field(default=None, max_length=150)
    note: str | None = Field(default=None, max_length=255)
    payment_method: PaymentMethod = "cash"


class ExpenseUpdate(BaseModel):
    """Shape of the JSON body for PUT /api/expenses/{id}.

    Same fields as create - PUT replaces the whole expense (except who
    owns it and how it was captured, which never change after the fact).
    """

    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    expense_date: date
    category_id: int | None = None
    merchant: str | None = Field(default=None, max_length=150)
    note: str | None = Field(default=None, max_length=255)
    payment_method: PaymentMethod = "cash"


class ExpenseOut(BaseModel):
    """An expense as returned to the client."""

    id: int
    amount: Decimal
    expense_date: date
    category_id: int | None
    merchant: str | None
    note: str | None
    payment_method: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseListOut(BaseModel):
    """Response for GET /api/expenses - a page of results plus enough
    info for the client to build pagination controls.
    """

    items: list[ExpenseOut]
    total: int
    page: int
    page_size: int
