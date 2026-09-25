from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import User
from app.schemas.report import MonthlyReportOut, TrendPoint
from app.services import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReportOut)
def get_monthly_report(
    month: str = Query(pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return report_service.monthly_report(db, current_user.id, month)


@router.get("/trend", response_model=list[TrendPoint])
def get_trend_report(
    months: int = Query(default=6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return report_service.trend_report(db, current_user.id, months)
