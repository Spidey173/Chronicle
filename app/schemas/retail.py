"""Retail domain schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# Location
class LocationResponse(BaseModel):
    id: int
    city: str
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None

    model_config = {"from_attributes": True}


# Category
class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


# Customer
class CustomerBase(BaseModel):
    customer_code: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    tier: str = "Bronze"


class CustomerResponse(CustomerBase):
    id: int
    location_id: Optional[int] = None
    location: Optional[LocationResponse] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Product
class ProductBase(BaseModel):
    product_code: str
    name: str
    unit_price: float
    cost_price: float = 0.0
    currency: str = "USD"
    stock_quantity: int = 0


class ProductResponse(ProductBase):
    id: int
    category_id: int
    category: Optional[CategoryResponse] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Order Item
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    unit_price: float
    discount: float
    tax: float
    item_total: float

    model_config = {"from_attributes": True}


# Order
class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    order_date: datetime
    status: str
    total_amount: float
    currency: str
    shipping_amount: float
    items: List[OrderItemResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
