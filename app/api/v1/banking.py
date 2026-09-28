"""Banking domain endpoints: transactions and accounts."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.banking import BankAccount, Transaction
from app.models.user import User
from app.schemas.banking import BankAccountResponse, TransactionResponse
from app.schemas.common import PaginatedResponse, PaginationMeta

router = APIRouter(prefix="", tags=["Banking Domain"])


@router.get("/transactions", response_model=PaginatedResponse[TransactionResponse])
def get_transactions(
    account_id: Optional[int] = Query(None, description="Filter by bank account ID"),
    category: Optional[str] = Query(None, description="Filter by category (Groceries, Dining, etc.)"),
    is_expense: Optional[bool] = Query(None, description="Filter expenses (true) or income (false)"),
    is_emi: Optional[bool] = Query(None, description="Filter EMI / Loan transactions"),
    start_date: Optional[datetime] = Query(None, description="Filter transactions from date"),
    end_date: Optional[datetime] = Query(None, description="Filter transactions up to date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve financial transactions with multi-criteria filtering."""
    query = db.query(Transaction)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if category:
        query = query.filter(Transaction.category.ilike(f"%{category.strip()}%"))
    if is_expense is not None:
        query = query.filter(Transaction.is_expense == is_expense)
    if is_emi is not None:
        query = query.filter(Transaction.is_emi == is_emi)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    query = query.order_by(Transaction.transaction_date.desc())

    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
    txns = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for t in txns:
        items.append(
            TransactionResponse(
                id=t.id,
                transaction_ref=t.transaction_ref,
                account_id=t.account_id,
                account_number=t.account.account_number if t.account else None,
                merchant_id=t.merchant_id,
                merchant_name=t.merchant.merchant_name if t.merchant else None,
                transaction_date=t.transaction_date,
                amount=t.amount,
                currency=t.currency,
                amount_usd=t.amount_usd,
                transaction_type=t.transaction_type,
                category=t.category,
                description=t.description,
                is_expense=t.is_expense,
                is_emi=t.is_emi,
                balance_after=t.balance_after,
                created_at=t.created_at,
            )
        )

    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return PaginatedResponse(items=items, pagination=pagination)


@router.get("/accounts", response_model=PaginatedResponse[BankAccountResponse])
def get_accounts(
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve bank accounts with balances and status."""
    query = db.query(BankAccount)
    if account_type:
        query = query.filter(BankAccount.account_type == account_type.title())

    query = query.order_by(BankAccount.id.asc())

    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
    accounts = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [BankAccountResponse.model_validate(a) for a in accounts]
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return PaginatedResponse(items=items, pagination=pagination)
