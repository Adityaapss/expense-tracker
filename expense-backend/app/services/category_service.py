"""Category business logic. Routers call these; they don't touch the
database directly.
"""
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.models import Category
from app.schemas.category import CategoryCreate


def list_categories(db: Session, user_id: int) -> list[Category]:
    """Default categories (user_id is NULL) plus this user's own."""
    stmt = select(Category).where(
        or_(Category.user_id.is_(None), Category.user_id == user_id)
    ).order_by(Category.user_id.is_(None).desc(), Category.name)
    return list(db.scalars(stmt))


def create_category(db: Session, user_id: int, data: CategoryCreate) -> Category:
    category = Category(name=data.name, icon=data.icon, user_id=user_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, user_id: int, category_id: int) -> None:
    category = db.get(Category, category_id)

    if category is None or category.user_id != user_id:
        # Same error whether it doesn't exist, is a default category, or
        # belongs to someone else - callers can't tell defaults/other
        # users' categories apart from categories that simply don't exist.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    db.delete(category)
    db.commit()
