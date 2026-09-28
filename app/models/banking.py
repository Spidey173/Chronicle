"""Banking domain normalized relational models."""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.database import Base


class BankAccount(Base):
    """Bank account dimension table."""

    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(50), unique=True, index=True, nullable=False)
    account_type = Column(String(50), nullable=False, index=True)  # Checking, Savings, Credit Card, Loan, Investment
    customer_name = Column(String(200), nullable=False, index=True)
    currency = Column(String(10), default="USD", nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    status = Column(String(20), default="Active", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class Merchant(Base):
    """Merchant dimension table."""

    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    merchant_name = Column(String(200), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    transactions = relationship("Transaction", back_populates="merchant")


class Transaction(Base):
    """Financial transaction fact table."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_ref = Column(String(64), unique=True, index=True, nullable=False)
    account_id = Column(Integer, ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="SET NULL"), nullable=True, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    amount_usd = Column(Float, nullable=False)  # Normalized amount in USD
    transaction_type = Column(String(20), nullable=False, index=True)  # Credit (Income), Debit (Expense)
    category = Column(String(100), nullable=False, index=True)         # Groceries, Utilities, Salary, Dining, EMI, etc.
    description = Column(String(255), nullable=True)
    is_expense = Column(Boolean, default=True, nullable=False, index=True)
    is_emi = Column(Boolean, default=False, nullable=False, index=True)
    balance_after = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    account = relationship("BankAccount", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
