"""Report business logic - read-only aggregations over a user's expenses.
Routers call these; they don't touch the database directly.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.models import Category, Expense
from app.schemas.report import CategoryBreakdown, MonthlyReportOut, TrendPoint
from app.services.date_utils import month_bounds


def monthly_report(db: Session, user_id: int, month: str) -> MonthlyReportOut:
    start, end = month_bounds(month)

    rows = db.execute(
        select(
            Expense.category_id,
            Category.name,
            func.sum(Expense.amount).label("total"),
        )
        .outerjoin(Category, Category.id == Expense.category_id)
        .where(
            Expense.user_id == user_id,
            Expense.expense_date.between(start, end),
        )
        .group_by(Expense.category_id, Category.name)
        .order_by(func.sum(Expense.amount).desc())
    ).all()

    by_category = [
        CategoryBreakdown(
            category_id=row.category_id,
            # A NULL category_id means the expense has no category assigned
            category_name=row.name or "Uncategorized",
            total=row.total,
        )
        for row in rows
    ]
    total = sum((row.total for row in rows), Decimal("0"))

    return MonthlyReportOut(month=month, total=total, by_category=by_category)


def _month_string(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def _months_back(months: int) -> list[str]:
    """List of 'YYYY-MM' strings, oldest first, ending with the current month."""
    today = date.today()
    base = today.year * 12 + (today.month - 1)  # months since year 0, 0-indexed
    result = []
    for i in range(months - 1, -1, -1):
        year, month0 = divmod(base - i, 12)
        result.append(_month_string(year, month0 + 1))
    return result


def trend_report(db: Session, user_id: int, months: int) -> list[TrendPoint]:
    points = []
    for month in _months_back(months):
        start, end = month_bounds(month)
        total = db.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.user_id == user_id,
                Expense.expense_date.between(start, end),
            )
        )
        points.append(TrendPoint(month=month, total=Decimal(total)))
    return points
