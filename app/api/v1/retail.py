"""Retail domain endpoints: orders, customers, and products."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.retail import Category, Customer, Order, OrderItem, Product
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.retail import (
    CustomerResponse,
    OrderItemResponse,
    OrderResponse,
    ProductResponse,
)

router = APIRouter(prefix="", tags=["Retail Domain"])


@router.get("/orders", response_model=PaginatedResponse[OrderResponse])
def get_orders(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Completed, Pending, etc.)"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    start_date: Optional[datetime] = Query(None, description="Filter orders from date"),
    end_date: Optional[datetime] = Query(None, description="Filter orders up to date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve orders with pagination and multi-criteria filtering."""
    query = db.query(Order)
    if status_filter:
        query = query.filter(Order.status == status_filter.title())
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    if start_date:
        query = query.filter(Order.order_date >= start_date)
    if end_date:
        query = query.filter(Order.order_date <= end_date)

    query = query.order_by(Order.order_date.desc())

    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
    orders = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for o in orders:
        cust_name = f"{o.customer.first_name} {o.customer.last_name}" if o.customer else None
        cust_email = o.customer.email if o.customer else None
        order_items = [
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name if item.product else None,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount,
                tax=item.tax,
                item_total=item.item_total,
            )
            for item in o.items
        ]
        items.append(
            OrderResponse(
                id=o.id,
                order_number=o.order_number,
                customer_id=o.customer_id,
                customer_name=cust_name,
                customer_email=cust_email,
                order_date=o.order_date,
                status=o.status,
                total_amount=o.total_amount,
                currency=o.currency,
                shipping_amount=o.shipping_amount,
                items=order_items,
                created_at=o.created_at,
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


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed order information by primary key."""
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found")

    cust_name = f"{o.customer.first_name} {o.customer.last_name}" if o.customer else None
    cust_email = o.customer.email if o.customer else None
    order_items = [
        OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name if item.product else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount=item.discount,
            tax=item.tax,
            item_total=item.item_total,
        )
        for item in o.items
    ]
    return OrderResponse(
        id=o.id,
        order_number=o.order_number,
        customer_id=o.customer_id,
        customer_name=cust_name,
        customer_email=cust_email,
        order_date=o.order_date,
        status=o.status,
        total_amount=o.total_amount,
        currency=o.currency,
        shipping_amount=o.shipping_amount,
        items=order_items,
        created_at=o.created_at,
    )


@router.get("/customers", response_model=PaginatedResponse[CustomerResponse])
def get_customers(
    tier: Optional[str] = Query(None, description="Filter by customer tier (Bronze, Silver, Gold, Platinum)"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve customers with tier filtering and search."""
    query = db.query(Customer)
    if tier:
        query = query.filter(Customer.tier == tier.title())
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (Customer.first_name.ilike(search_fmt))
            | (Customer.last_name.ilike(search_fmt))
            | (Customer.email.ilike(search_fmt))
        )

    query = query.order_by(Customer.created_at.desc())

    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
    customers = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [CustomerResponse.model_validate(c) for c in customers]
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return PaginatedResponse(items=items, pagination=pagination)


@router.get("/products", response_model=PaginatedResponse[ProductResponse])
def get_products(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search product name or code"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve products catalog with category filtering and keyword search."""
    query = db.query(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter((Product.name.ilike(search_fmt)) | (Product.product_code.ilike(search_fmt)))

    query = query.order_by(Product.name.asc())

    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
    products = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [ProductResponse.model_validate(p) for p in products]
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return PaginatedResponse(items=items, pagination=pagination)
