"""seed default categories

Revision ID: e908047d0fb3
Revises: 8c298158630e
Create Date: 2026-09-25 18:16:44.728123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e908047d0fb3'
down_revision: Union[str, Sequence[str], None] = '8c298158630e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Lightweight stand-in for the categories table, just for this insert.
# We don't import the real ORM model here on purpose: migrations should
# stay correct even if the model changes shape later.
categories_table = sa.table(
    "categories",
    sa.column("name", sa.String),
    sa.column("icon", sa.String),
    sa.column("user_id", sa.Integer),
)

DEFAULT_CATEGORIES = [
    {"name": "Food", "icon": "utensils"},
    {"name": "Education", "icon": "book"},
    {"name": "Entertainment", "icon": "film"},
    {"name": "Travel", "icon": "plane"},
    {"name": "Bills", "icon": "receipt"},
    {"name": "Shopping", "icon": "shopping-bag"},
    {"name": "Health", "icon": "heart-pulse"},
    {"name": "Groceries", "icon": "shopping-cart"},
    {"name": "Rent", "icon": "home"},
    {"name": "Other", "icon": "tag"},
]


def upgrade() -> None:
    """Insert the default (user_id = NULL) categories shared by everyone."""
    op.bulk_insert(
        categories_table,
        [{**c, "user_id": None} for c in DEFAULT_CATEGORIES],
    )


def downgrade() -> None:
    """Remove exactly the default categories this migration added."""
    names = tuple(c["name"] for c in DEFAULT_CATEGORIES)
    op.execute(
        categories_table.delete()
        .where(categories_table.c.user_id.is_(None))
        .where(categories_table.c.name.in_(names))
    )
