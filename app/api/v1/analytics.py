"""Analytics endpoints exposing business insights and data quality telemetry."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.analytics import (
    BankingSummaryResponse,
    CategorySummaryItem,
    DashboardSummaryResponse,
    DataQualityMetrics,
    MonthlySalesItem,
    RevenueAnalytics,
    TopCustomerItem,
    TopProductItem,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard-summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Retrieve complete unified dashboard metrics in a single fast call."""
    return AnalyticsService.get_dashboard_summary(db)


@router.get("/top-products", response_model=List[TopProductItem])
def get_top_products(
    limit: int = Query(10, ge=1, le=100, description="Number of top products to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve top-selling products ranked by total revenue."""
    return AnalyticsService.get_top_products(db, limit=limit)


@router.get("/monthly-sales", response_model=List[MonthlySalesItem])
def get_monthly_sales(
    year: Optional[int] = Query(None, description="Filter for specific year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve sales revenue and order counts broken down by month."""
    return AnalyticsService.get_monthly_sales(db, year=year)


@router.get("/top-customers", response_model=List[TopCustomerItem])
def get_top_customers(
    limit: int = Query(10, ge=1, le=100, description="Number of top customers to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve highest-value customers ranked by cumulative spend."""
    return AnalyticsService.get_top_customers(db, limit=limit)


@router.get("/revenue", response_model=RevenueAnalytics)
def get_revenue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve aggregate revenue metrics, average order value, and gross margins."""
    return AnalyticsService.get_revenue_analytics(db)


@router.get("/category-summary", response_model=List[CategorySummaryItem])
def get_category_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve sales performance and unit distribution broken down by product category."""
    return AnalyticsService.get_category_summary(db)


@router.get("/banking-summary", response_model=BankingSummaryResponse)
def get_banking_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve banking analytics: income vs expenses, savings rate, EMI payments, and category spending."""
    return AnalyticsService.get_banking_summary(db)


@router.get("/data-quality", response_model=DataQualityMetrics)
def get_data_quality(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve pipeline data quality metrics, validation pass rates, and rejection causes."""
    return AnalyticsService.get_data_quality_metrics(db)
