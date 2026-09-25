from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    expenses: Mapped[list["Expense"]] = relationship(back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    icon: Mapped[str | None] = mapped_column(String(50))
    # NULL user_id = default category shared by everyone
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    expense_date: Mapped[date] = mapped_column(index=True)
    merchant: Mapped[str | None] = mapped_column(String(150))
    note: Mapped[str | None] = mapped_column(String(255))
    payment_method: Mapped[str] = mapped_column(String(20), default="cash")  # cash / upi / card
    source: Mapped[str] = mapped_column(String(20), default="manual")        # manual / sms / notification / statement
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="expenses")
    category: Mapped["Category"] = relationship()


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (UniqueConstraint("user_id", "category_id", "month"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    month: Mapped[str] = mapped_column(String(7))  # "2026-09"
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
