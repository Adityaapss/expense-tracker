from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import User
from app.schemas.expense import ExpenseCreate, ExpenseListOut, ExpenseOut, ExpenseUpdate
from app.services import expense_service
from app.services.expense_service import PAGE_SIZE

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.get("", response_model=ExpenseListOut)
def get_expenses(
    month: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    category_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = expense_service.list_expenses(
        db, current_user.id, month, category_id, page
    )
    return ExpenseListOut(items=items, total=total, page=page, page_size=PAGE_SIZE)


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expense_service.create_expense(db, current_user.id, data)


@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expense_service.update_expense(db, current_user.id, expense_id, data)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense_service.delete_expense(db, current_user.id, expense_id)
