"""Budget business logic. Routers call these; they don't touch the
database directly.
"""
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.models import Budget, Category, Expense
from app.schemas.budget import BudgetCreate, BudgetOut
from app.services.date_utils import month_bounds

WARNING_THRESHOLD = 80
OVER_THRESHOLD = 100


def _ensure_category_is_usable(db: Session, user_id: int, category_id: int) -> None:
    """A category must be a default (user_id NULL) or belong to this user."""
    category = db.get(Category, category_id)
    if category is None or (category.user_id is not None and category.user_id != user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )


def _spent_for(db: Session, user_id: int, category_id: int, month: str) -> Decimal:
    start, end = month_bounds(month)
    total = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.user_id == user_id,
            Expense.category_id == category_id,
            Expense.expense_date.between(start, end),
        )
    )
    return Decimal(total)


def _status_for(percent_used: float) -> str:
    if percent_used >= OVER_THRESHOLD:
        return "over"
    if percent_used >= WARNING_THRESHOLD:
        return "warning"
    return "ok"


def _to_out(db: Session, user_id: int, budget: Budget) -> BudgetOut:
    spent = _spent_for(db, user_id, budget.category_id, budget.month)
    percent_used = round(float(spent / budget.amount * 100), 1)
    return BudgetOut(
        id=budget.id,
        category_id=budget.category_id,
        month=budget.month,
        amount=budget.amount,
        spent=spent,
        percent_used=percent_used,
        status=_status_for(percent_used),
    )


def list_budgets(db: Session, user_id: int, month: str) -> list[BudgetOut]:
    stmt = select(Budget).where(Budget.user_id == user_id, Budget.month == month)
    budgets = list(db.scalars(stmt))
    return [_to_out(db, user_id, b) for b in budgets]


def create_or_update_budget(
    db: Session, user_id: int, data: BudgetCreate
) -> tuple[BudgetOut, bool]:
    """Create the budget for this (category, month), or update the amount
    if one already exists. Returns (budget, was_created).
    """
    _ensure_category_is_usable(db, user_id, data.category_id)

    existing = db.scalar(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == data.category_id,
            Budget.month == data.month,
        )
    )

    if existing is not None:
        existing.amount = data.amount
        budget = existing
        was_created = False
    else:
        budget = Budget(
            user_id=user_id,
            category_id=data.category_id,
            month=data.month,
            amount=data.amount,
        )
        db.add(budget)
        was_created = True

    db.commit()
    db.refresh(budget)
    return _to_out(db, user_id, budget), was_created
