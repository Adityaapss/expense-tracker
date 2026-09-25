from decimal import Decimal

from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    """How much was spent in one category, for the pie-chart data."""

    category_id: int | None
    category_name: str
    total: Decimal


class MonthlyReportOut(BaseModel):
    """Response for GET /api/reports/monthly."""

    month: str
    total: Decimal
    by_category: list[CategoryBreakdown]


class TrendPoint(BaseModel):
    """One point on the month-by-month trend (bar chart) line."""

    month: str
    total: Decimal
