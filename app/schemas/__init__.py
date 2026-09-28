"""Schemas module export."""

from app.schemas.auth import Token, TokenPayload, UserBase, UserCreate, UserLogin, UserResponse
from app.schemas.common import (
    HealthResponse,
    IngestionBatchResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationMeta,
    RejectedRecordResponse,
)
from app.schemas.retail import (
    CategoryResponse,
    CustomerBase,
    CustomerResponse,
    LocationResponse,
    OrderItemResponse,
    OrderResponse,
    ProductBase,
    ProductResponse,
)
from app.schemas.banking import BankAccountResponse, MerchantResponse, TransactionResponse
from app.schemas.analytics import (
    BankingSummaryResponse,
    CategorySummaryItem,
    DashboardSummaryResponse,
    DataQualityMetrics,
    MonthlySalesItem,
    RevenueAnalytics,
    SpendingByCategoryItem,
    TopCustomerItem,
    TopProductItem,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenPayload",
    "MessageResponse",
    "PaginationMeta",
    "PaginatedResponse",
    "IngestionBatchResponse",
    "RejectedRecordResponse",
    "HealthResponse",
    "LocationResponse",
    "CategoryResponse",
    "CustomerBase",
    "CustomerResponse",
    "ProductBase",
    "ProductResponse",
    "OrderItemResponse",
    "OrderResponse",
    "BankAccountResponse",
    "MerchantResponse",
    "TransactionResponse",
    "TopProductItem",
    "MonthlySalesItem",
    "TopCustomerItem",
    "RevenueAnalytics",
    "CategorySummaryItem",
    "SpendingByCategoryItem",
    "BankingSummaryResponse",
    "DataQualityMetrics",
    "DashboardSummaryResponse",
]
