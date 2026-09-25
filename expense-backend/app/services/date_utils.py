"""Shared date helpers used by any service that filters by a 'YYYY-MM'
month string (expenses, budgets, and later reports).
"""
import calendar
from datetime import date


def month_bounds(month: str) -> tuple[date, date]:
    """Turn 'YYYY-MM' into the first and last calendar day of that month."""
    year, month_num = (int(part) for part in month.split("-"))
    last_day = calendar.monthrange(year, month_num)[1]
    return date(year, month_num, 1), date(year, month_num, last_day)
