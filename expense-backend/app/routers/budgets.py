from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import User
from app.schemas.budget import BudgetCreate, BudgetOut
from app.services import budget_service

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetOut])
def get_budgets(
    month: str = Query(pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return budget_service.list_budgets(db, current_user.id, month)


@router.post("", response_model=BudgetOut)
def create_budget(
    data: BudgetCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget, was_created = budget_service.create_or_update_budget(db, current_user.id, data)
    response.status_code = status.HTTP_201_CREATED if was_created else status.HTTP_200_OK
    return budget
