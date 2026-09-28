"""Analytics service providing aggregation and performance metrics."""

from collections import Counter
import calendar
from typing import Dict, List, Optional
from sqlalchemy import case, distinct, extract, func
from sqlalchemy.orm import Session

from app.models.banking import BankAccount, Transaction
from app.models.common import IngestionBatch, RejectedRecord
from app.models.retail import Category, Customer, Location, Order, OrderItem, Product
from app.schemas.analytics import (
    BankingSummaryResponse,
    CategorySummaryItem,
    DashboardSummaryResponse,
    DataQualityMetrics,
    MonthlySalesItem,
    ProductAreaSalesItem,
    ProductAreaSalesResponse,
    RevenueAnalytics,
    SpendingByCategoryItem,
    TopCustomerItem,
    TopProductItem,
)


class AnalyticsService:
    """Calculates enterprise business metrics for retail and banking domains."""

    @staticmethod
    def get_top_products(db: Session, limit: int = 10) -> List[TopProductItem]:
        results = (
            db.query(
                Product.id.label("product_id"),
                Product.product_code.label("product_code"),
                Product.name.label("product_name"),
                Category.name.label("category_name"),
                func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold"),
                func.coalesce(func.sum(OrderItem.item_total), 0.0).label("total_revenue"),
            )
            .join(Category, Product.category_id == Category.id)
            .outerjoin(OrderItem, Product.id == OrderItem.product_id)
            .group_by(Product.id, Product.product_code, Product.name, Category.name)
            .order_by(func.sum(OrderItem.item_total).desc())
            .limit(limit)
            .all()
        )

        return [
            TopProductItem(
                product_id=r.product_id,
                product_code=r.product_code,
                product_name=r.product_name,
                category_name=r.category_name,
                units_sold=int(r.units_sold),
                total_revenue=round(float(r.total_revenue), 2),
            )
            for r in results
        ]

    @staticmethod
    def get_product_sales_by_area(
        db: Session,
        product_name: Optional[str] = None,
        limit: int = 10,
    ) -> ProductAreaSalesResponse:
        """Find which geographic place/area has the highest sales for a product (e.g. iPhone on Amazon)."""
        query = (
            db.query(
                Location.city.label("city"),
                Location.state.label("state"),
                Location.country.label("country"),
                Product.name.label("product_name"),
                func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold"),
                func.coalesce(func.sum(OrderItem.item_total), 0.0).label("total_sales"),
            )
            .join(Customer, Customer.location_id == Location.id)
            .join(Order, Order.customer_id == Customer.id)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .join(Product, OrderItem.product_id == Product.id)
        )

        if product_name:
            query = query.filter(Product.name.ilike(f"%{product_name}%"))

        results = (
            query.group_by(Location.city, Location.state, Location.country, Product.name)
            .order_by(func.sum(OrderItem.item_total).desc())
            .limit(limit)
            .all()
        )

        rankings = [
            ProductAreaSalesItem(
                city=r.city,
                state=r.state,
                country=r.country,
                product_name=r.product_name,
                units_sold=int(r.units_sold),
                total_sales=round(float(r.total_sales), 2),
                currency="USD",
            )
            for r in results
        ]

        top_area = rankings[0].city if rankings else None
        return ProductAreaSalesResponse(
            product_filter=product_name,
            top_area=top_area,
            rankings=rankings,
        )

    @staticmethod
    def get_monthly_sales(db: Session, year: Optional[int] = None) -> List[MonthlySalesItem]:
        # Support extracting year and month across PostgreSQL and SQLite
        query = db.query(
            extract("year", Order.order_date).label("year"),
            extract("month", Order.order_date).label("month"),
            func.count(distinct(Order.id)).label("order_count"),
            func.coalesce(func.sum(Order.total_amount), 0.0).label("total_revenue"),
        )
        if year:
            query = query.filter(extract("year", Order.order_date) == year)

        results = (
            query.group_by(extract("year", Order.order_date), extract("month", Order.order_date))
            .order_by(extract("year", Order.order_date).asc(), extract("month", Order.order_date).asc())
            .all()
        )

        monthly_items = []
        for r in results:
            y = int(r.year) if r.year else 2026
            m = int(r.month) if r.month else 1
            rev = round(float(r.total_revenue), 2)
            orders = int(r.order_count)
            aov = round(rev / orders, 2) if orders > 0 else 0.0
            month_name = calendar.month_name[m] if 1 <= m <= 12 else f"Month {m}"

            monthly_items.append(
                MonthlySalesItem(
                    year=y,
                    month=m,
                    month_name=month_name,
                    order_count=orders,
                    total_revenue=rev,
                    average_order_value=aov,
                )
            )
        return monthly_items

    @staticmethod
    def get_top_customers(db: Session, limit: int = 10) -> List[TopCustomerItem]:
        results = (
            db.query(
                Customer.id.label("customer_id"),
                Customer.customer_code.label("customer_code"),
                (Customer.first_name + " " + Customer.last_name).label("customer_name"),
                Customer.email.label("email"),
                Customer.tier.label("tier"),
                func.count(distinct(Order.id)).label("orders_count"),
                func.coalesce(func.sum(Order.total_amount), 0.0).label("total_spent"),
            )
            .outerjoin(Order, Customer.id == Order.customer_id)
            .group_by(Customer.id, Customer.customer_code, Customer.first_name, Customer.last_name, Customer.email, Customer.tier)
            .order_by(func.sum(Order.total_amount).desc())
            .limit(limit)
            .all()
        )

        return [
            TopCustomerItem(
                customer_id=r.customer_id,
                customer_code=r.customer_code,
                customer_name=r.customer_name,
                email=r.email,
                tier=r.tier,
                orders_count=int(r.orders_count),
                total_spent=round(float(r.total_spent), 2),
            )
            for r in results
        ]

    @staticmethod
    def get_revenue_analytics(db: Session) -> RevenueAnalytics:
        order_stats = db.query(
            func.coalesce(func.sum(Order.total_amount), 0.0).label("total_revenue"),
            func.count(Order.id).label("total_orders"),
        ).first()

        items_stats = db.query(
            func.coalesce(func.sum(OrderItem.quantity), 0).label("items_sold"),
            func.coalesce(func.sum(OrderItem.quantity * Product.cost_price), 0.0).label("total_cogs"),
        ).join(Product, OrderItem.product_id == Product.id).first()

        # Revenue by status
        status_results = (
            db.query(Order.status, func.coalesce(func.sum(Order.total_amount), 0.0))
            .group_by(Order.status)
            .all()
        )
        status_map = {str(status): round(float(amt), 2) for status, amt in status_results}

        total_rev = round(float(order_stats.total_revenue), 2) if order_stats else 0.0
        total_orders = int(order_stats.total_orders) if order_stats else 0
        total_items = int(items_stats.items_sold) if items_stats else 0
        total_cogs = float(items_stats.total_cogs) if items_stats else 0.0

        aov = round(total_rev / total_orders, 2) if total_orders > 0 else 0.0
        gross_profit = round(total_rev - total_cogs, 2)

        return RevenueAnalytics(
            total_revenue=total_rev,
            total_orders=total_orders,
            total_items_sold=total_items,
            average_order_value=aov,
            estimated_gross_profit=gross_profit,
            currency="USD",
            revenue_by_status=status_map,
        )

    @staticmethod
    def get_category_summary(db: Session) -> List[CategorySummaryItem]:
        total_rev_all = (
            db.query(func.coalesce(func.sum(OrderItem.item_total), 0.0)).scalar() or 0.0
        )

        results = (
            db.query(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.count(distinct(Product.id)).label("products_count"),
                func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold"),
                func.coalesce(func.sum(OrderItem.item_total), 0.0).label("total_revenue"),
            )
            .outerjoin(Product, Category.id == Product.category_id)
            .outerjoin(OrderItem, Product.id == OrderItem.product_id)
            .group_by(Category.id, Category.name)
            .order_by(func.sum(OrderItem.item_total).desc())
            .all()
        )

        summary_items = []
        for r in results:
            rev = round(float(r.total_revenue), 2)
            pct = round((rev / total_rev_all * 100), 2) if total_rev_all > 0 else 0.0
            summary_items.append(
                CategorySummaryItem(
                    category_id=r.category_id,
                    category_name=r.category_name,
                    products_count=int(r.products_count),
                    units_sold=int(r.units_sold),
                    total_revenue=rev,
                    percentage_of_total=pct,
                )
            )
        return summary_items

    @staticmethod
    def get_banking_summary(db: Session) -> BankingSummaryResponse:
        # Income (is_expense = False) vs Expense (is_expense = True)
        income_val = (
            db.query(func.coalesce(func.sum(Transaction.amount_usd), 0.0))
            .filter(Transaction.is_expense == False)
            .scalar()
            or 0.0
        )
        expense_val = (
            db.query(func.coalesce(func.sum(Transaction.amount_usd), 0.0))
            .filter(Transaction.is_expense == True)
            .scalar()
            or 0.0
        )
        emi_val = (
            db.query(func.coalesce(func.sum(Transaction.amount_usd), 0.0))
            .filter(Transaction.is_emi == True)
            .scalar()
            or 0.0
        )
        total_txns = db.query(func.count(Transaction.id)).scalar() or 0

        net_savings = round(income_val - expense_val, 2)
        savings_rate = round((net_savings / income_val * 100), 2) if income_val > 0 else 0.0

        # Spending by category (Debit/Expenses)
        cat_results = (
            db.query(
                Transaction.category,
                func.count(Transaction.id).label("count"),
                func.coalesce(func.sum(Transaction.amount_usd), 0.0).label("total"),
            )
            .filter(Transaction.is_expense == True)
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount_usd).desc())
            .all()
        )

        spending_items = []
        for r in cat_results:
            amt = round(float(r.total), 2)
            pct = round((amt / expense_val * 100), 2) if expense_val > 0 else 0.0
            spending_items.append(
                SpendingByCategoryItem(
                    category=r.category,
                    transaction_count=int(r.count),
                    total_amount_usd=amt,
                    percentage=pct,
                )
            )

        # Transactions by type
        type_results = (
            db.query(Transaction.transaction_type, func.coalesce(func.sum(Transaction.amount_usd), 0.0))
            .group_by(Transaction.transaction_type)
            .all()
        )
        type_map = {t: round(float(a), 2) for t, a in type_results}

        # Available balance across active accounts
        balance_val = (
            db.query(func.coalesce(func.sum(BankAccount.balance), 0.0))
            .filter(BankAccount.status == "Active")
            .scalar()
            or 0.0
        )

        return BankingSummaryResponse(
            total_income_usd=round(income_val, 2),
            total_expenses_usd=round(expense_val, 2),
            monthly_spending_usd=round(expense_val, 2),
            net_savings_usd=net_savings,
            savings_rate_percentage=savings_rate,
            total_emi_paid_usd=round(emi_val, 2),
            available_balance_usd=round(balance_val, 2),
            total_transactions=total_txns,
            spending_by_category=spending_items,
            transactions_by_type=type_map,
        )

    @staticmethod
    def get_data_quality_metrics(db: Session) -> DataQualityMetrics:
        batches = db.query(IngestionBatch).all()
        total_processed = sum(b.total_records for b in batches)
        total_valid = sum(b.valid_records for b in batches)
        total_rejected = sum(b.rejected_records for b in batches)

        quality_pct = round((total_valid / total_processed * 100), 2) if total_processed > 0 else 100.0

        # Domain breakdown
        domain_counts: Dict[str, int] = {}
        for b in batches:
            domain_counts[b.domain] = domain_counts.get(b.domain, 0) + b.rejected_records

        # Rejection reasons aggregation
        rejected_recs = db.query(RejectedRecord).limit(500).all()
        reason_counter = Counter()
        for rec in rejected_recs:
            for reason in rec.get_reasons():
                # Extract clean prefix
                prefix = reason.split(":")[0] if ":" in reason else reason
                reason_counter[prefix] += 1

        top_reasons = [{k: v} for k, v in reason_counter.most_common(8)]

        return DataQualityMetrics(
            total_batches=len(batches),
            total_records_processed=total_processed,
            total_valid_records=total_valid,
            total_rejected_records=total_rejected,
            overall_quality_percentage=quality_pct,
            rejections_by_domain=domain_counts,
            top_rejection_reasons=top_reasons,
        )

    @staticmethod
    def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
        return DashboardSummaryResponse(
            revenue=AnalyticsService.get_revenue_analytics(db),
            data_quality=AnalyticsService.get_data_quality_metrics(db),
            banking=AnalyticsService.get_banking_summary(db),
            monthly_sales=AnalyticsService.get_monthly_sales(db),
            categories=AnalyticsService.get_category_summary(db),
            top_products=AnalyticsService.get_top_products(db, limit=5),
            top_customers=AnalyticsService.get_top_customers(db, limit=5),
        )
