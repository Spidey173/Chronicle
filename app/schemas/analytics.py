"""Analytics response schemas for retail and banking domains."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class TopProductItem(BaseModel):
    product_id: int
    product_code: str
    product_name: str
    category_name: str
    units_sold: int
    total_revenue: float


class MonthlySalesItem(BaseModel):
    year: int
    month: int
    month_name: str
    order_count: int
    total_revenue: float
    average_order_value: float


class TopCustomerItem(BaseModel):
    customer_id: int
    customer_code: str
    customer_name: str
    email: str
    tier: str
    orders_count: int
    total_spent: float


class RevenueAnalytics(BaseModel):
    total_revenue: float
    total_orders: int
    total_items_sold: int
    average_order_value: float
    estimated_gross_profit: float
    currency: str = "USD"
    revenue_by_status: Dict[str, float]


class CategorySummaryItem(BaseModel):
    category_id: int
    category_name: str
    products_count: int
    units_sold: int
    total_revenue: float
    percentage_of_total: float


class SpendingByCategoryItem(BaseModel):
    category: str
    transaction_count: int
    total_amount_usd: float
    percentage: float


class ProductAreaSalesItem(BaseModel):
    city: str
    state: Optional[str] = None
    country: str
    product_name: str
    units_sold: int
    total_sales: float
    currency: str = "USD"


class ProductAreaSalesResponse(BaseModel):
    product_filter: Optional[str] = None
    top_area: Optional[str] = None
    rankings: List[ProductAreaSalesItem]


class BankingSummaryResponse(BaseModel):
    total_income_usd: float
    total_expenses_usd: float
    monthly_spending_usd: float
    net_savings_usd: float
    savings_rate_percentage: float
    total_emi_paid_usd: float
    available_balance_usd: float
    total_transactions: int
    spending_by_category: List[SpendingByCategoryItem]
    transactions_by_type: Dict[str, float]


class DataQualityMetrics(BaseModel):
    total_batches: int
    total_records_processed: int
    total_valid_records: int
    total_rejected_records: int
    overall_quality_percentage: float
    rejections_by_domain: Dict[str, int]
    top_rejection_reasons: List[Dict[str, int]]


class DashboardSummaryResponse(BaseModel):
    revenue: RevenueAnalytics
    data_quality: DataQualityMetrics
    banking: BankingSummaryResponse
    monthly_sales: List[MonthlySalesItem]
    categories: List[CategorySummaryItem]
    top_products: List[TopProductItem]
    top_customers: List[TopCustomerItem]
