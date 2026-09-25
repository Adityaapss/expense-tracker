"""Expense business logic. Routers call these; they don't touch the
database directly.

Every function here takes user_id and filters by it - a user must never
see or change another user's expenses.
"""
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.models import Category, Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services.date_utils import month_bounds

PAGE_SIZE = 20


def _ensure_category_is_usable(db: Session, user_id: int, category_id: int) -> None:
    """A category must be a default (user_id NULL) or belong to this user."""
    category = db.get(Category, category_id)
    if category is None or (category.user_id is not None and category.user_id != user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )


def list_expenses(
    db: Session,
    user_id: int,
    month: str | None,
    category_id: int | None,
    page: int,
) -> tuple[list[Expense], int]:
    stmt = select(Expense).where(Expense.user_id == user_id)

    if month is not None:
        start, end = month_bounds(month)
        stmt = stmt.where(Expense.expense_date.between(start, end))

    if category_id is not None:
        stmt = stmt.where(Expense.category_id == category_id)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = (
        stmt.order_by(Expense.expense_date.desc(), Expense.created_at.desc())
        .offset((page - 1) * PAGE_SIZE)
        .limit(PAGE_SIZE)
    )
    items = list(db.scalars(stmt))
    return items, total


def create_expense(db: Session, user_id: int, data: ExpenseCreate) -> Expense:
    if data.category_id is not None:
        _ensure_category_is_usable(db, user_id, data.category_id)

    expense = Expense(
        user_id=user_id,
        category_id=data.category_id,
        amount=data.amount,
        expense_date=data.expense_date,
        merchant=data.merchant,
        note=data.note,
        payment_method=data.payment_method,
        source="manual",
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def _get_owned_expense(db: Session, user_id: int, expense_id: int) -> Expense:
    expense = db.get(Expense, expense_id)
    if expense is None or expense.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )
    return expense


def update_expense(
    db: Session, user_id: int, expense_id: int, data: ExpenseUpdate
) -> Expense:
    expense = _get_owned_expense(db, user_id, expense_id)

    if data.category_id is not None:
        _ensure_category_is_usable(db, user_id, data.category_id)

    expense.amount = data.amount
    expense.expense_date = data.expense_date
    expense.category_id = data.category_id
    expense.merchant = data.merchant
    expense.note = data.note
    expense.payment_method = data.payment_method

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, user_id: int, expense_id: int) -> None:
    expense = _get_owned_expense(db, user_id, expense_id)
    db.delete(expense)
    db.commit()
