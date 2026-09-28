"""Banking domain schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BankAccountResponse(BaseModel):
    id: int
    account_number: str
    account_type: str
    customer_name: str
    currency: str
    balance: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MerchantResponse(BaseModel):
    id: int
    merchant_name: str
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionResponse(BaseModel):
    id: int
    transaction_ref: str
    account_id: int
    account_number: Optional[str] = None
    merchant_id: Optional[int] = None
    merchant_name: Optional[str] = None
    transaction_date: datetime
    amount: float
    currency: str
    amount_usd: float
    transaction_type: str
    category: str
    description: Optional[str] = None
    is_expense: bool
    is_emi: bool
    balance_after: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}
