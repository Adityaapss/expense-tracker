from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

BudgetStatus = Literal["ok", "warning", "over"]


class BudgetCreate(BaseModel):
    """Shape of the JSON body for POST /api/budgets."""

    category_id: int
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class BudgetOut(BaseModel):
    """A budget plus how much of it has been spent so far.

    spent/percent_used/status aren't columns on the Budget table - they're
    computed fresh from the user's expenses every time this is returned,
    so they're always up to date.
    """

    id: int
    category_id: int
    month: str
    amount: Decimal
    spent: Decimal
    percent_used: float
    status: BudgetStatus
