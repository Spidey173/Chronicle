# API Documentation: Chronicle REST Services

The Chronicle API exposes real-time data ingestion, relational queries, enterprise analytics, and health diagnostics over HTTP.

* **Base URL**: `http://localhost:8000` or `http://localhost:8000/api/v1`
* **Interactive Swagger UI**: `http://localhost:8000/docs`
* **Interactive ReDoc UI**: `http://localhost:8000/redoc`

---

## Authentication

All endpoints (except `/health`, `/auth/register`, and `/auth/login`) require a Bearer token in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_access_token>
```

### 1. User Registration
`POST /api/v1/auth/register`

**Request Body:**
```json
{
  "email": "analyst@example.com",
  "password": "SecurePassword123!",
  "full_name": "Senior Analyst",
  "role": "user"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "email": "analyst@example.com",
  "full_name": "Senior Analyst",
  "role": "user",
  "is_active": true,
  "created_at": "2026-09-28T10:00:00Z"
}
```

### 2. User Login
`POST /api/v1/auth/login`

**Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "AdminSecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in_minutes": 1440,
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "full_name": "System Administrator",
    "role": "admin",
    "is_active": true
  }
}
```

---

## Data Ingestion & File Upload

### 3. File Upload Ingestion
`POST /upload` or `POST /api/v1/upload`

Multipart form data upload supporting CSV, Excel (`.xlsx`, `.xls`), and JSON files. Automatically executes the complete Extract -> Validate -> Transform -> Load pipeline.

**Form Parameters:**
* `file`: Binary file upload
* `domain`: `retail` or `banking` (Default: `retail`)

**Response (200 OK):**
```json
{
  "batch_id": "426b38c2-4a0b-4d40-9a25-c637ef60de44",
  "domain": "retail",
  "source_name": "sales_feed.csv",
  "status": "completed",
  "total_records": 100,
  "valid_records": 94,
  "rejected_records": 6,
  "data_quality_pct": 94.0,
  "rule_violations": {
    "invalid_email": 3,
    "duplicate_records": 2,
    "incorrect_numeric": 1
  },
  "entities_affected": {
    "orders": 85,
    "order_items": 94,
    "customers": 40,
    "products": 12
  },
  "execution_time_sec": 0.428
}
```

### 4. Inspect Ingestion Batches
`GET /api/v1/ingestion/batches`

**Query Parameters:**
* `domain`: Filter by domain (`retail`, `banking`)
* `status`: Filter by status (`completed`, `failed`)
* `page`: Page number (default: 1)
* `page_size`: Records per page (default: 20, max: 100)

### 5. Dead-Letter Quarantine Queue
`GET /api/v1/ingestion/quarantine`

Inspect records rejected during validation along with reason codes.

**Query Parameters:**
* `batch_id`: Filter by specific execution batch UUID
* `domain`: Filter by domain

---

## Retail & E-Commerce Endpoints

### 6. List Orders
`GET /orders` or `GET /api/v1/orders`

**Query Parameters:**
* `status`: `Completed`, `Pending`, `Cancelled`
* `customer_id`: Filter by customer ID
* `start_date`: ISO datetime
* `end_date`: ISO datetime
* `page`, `page_size`: Pagination

### 7. List Customers
`GET /customers` or `GET /api/v1/customers`

**Query Parameters:**
* `tier`: `Bronze`, `Silver`, `Gold`, `Platinum`
* `search`: Search name or email

### 8. List Products
`GET /products` or `GET /api/v1/products`

**Query Parameters:**
* `category_id`: Filter by category
* `search`: Keyword search for product name or code

---

## Banking Endpoints

### 9. List Transactions
`GET /transactions` or `GET /api/v1/transactions`

**Query Parameters:**
* `account_id`: Filter by account ID
* `category`: Filter by category (e.g. `Groceries`, `Dining`, `Utilities`)
* `is_expense`: `true` for debits, `false` for credits
* `is_emi`: `true` for loan/mortgage payments

### 10. List Bank Accounts
`GET /accounts` or `GET /api/v1/accounts`

**Query Parameters:**
* `account_type`: `Checking`, `Savings`, `Loan`, `Credit Card`

---

## Enterprise Analytics Endpoints

### 11. Top Selling Products
`GET /analytics/top-products?limit=10`

### 12. Monthly Sales Velocity
`GET /analytics/monthly-sales?year=2026`

### 13. Top Customers by Lifetime Spend
`GET /analytics/top-customers?limit=10`

### 14. Revenue & Margin Summary
`GET /analytics/revenue`

**Sample Response:**
```json
{
  "total_revenue": 142580.50,
  "total_orders": 312,
  "total_items_sold": 894,
  "average_order_value": 457.00,
  "estimated_gross_profit": 61200.25,
  "currency": "USD",
  "revenue_by_status": {
    "Completed": 138000.00,
    "Pending": 4580.50
  }
}
```

### 15. Category Sales Summary
`GET /analytics/category-summary`

### 16. Banking Financial Telemetry
`GET /analytics/banking-summary`

Returns income vs expenses, savings rate, EMI loan payments, and category spending distribution.

### 17. Data Quality & Pipeline Health
`GET /analytics/data-quality`

---

## Health Check

### 18. Health & Readiness Probe
`GET /health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "environment": "production",
  "database": "healthy",
  "timestamp": "2026-09-28T12:00:00Z",
  "version": "1.0.0"
}
```
