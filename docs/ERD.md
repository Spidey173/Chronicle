# Entity-Relationship Diagram (ERD) & Database Schema

This document details the normalized relational database schema powering the Chronicle platform.

---

## 1. Relational ER Diagram

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : performs
    INGESTION_BATCHES ||--o{ REJECTED_RECORDS : quarantines

    LOCATIONS ||--o{ CUSTOMERS : locates
    CATEGORIES ||--o{ PRODUCTS : categorizes
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : ordered_in

    BANK_ACCOUNTS ||--o{ TRANSACTIONS : holds
    MERCHANTS ||--o{ TRANSACTIONS : receives

    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK
        string action
        string entity_type
        string entity_id
        text details
        string ip_address
        datetime created_at
    }

    INGESTION_BATCHES {
        int id PK
        string batch_id UK
        string domain
        string source_type
        string source_name
        string status
        int total_records
        int valid_records
        int rejected_records
        datetime started_at
        datetime completed_at
        float execution_time_sec
        text metadata_json
    }

    REJECTED_RECORDS {
        int id PK
        string batch_id FK
        string domain
        string source_identifier
        int record_index
        text raw_data_json
        text rejection_reasons_json
        datetime created_at
    }

    LOCATIONS {
        int id PK
        string city
        string state
        string country
        string postal_code
    }

    CATEGORIES {
        int id PK
        string name UK
        string slug UK
        text description
    }

    CUSTOMERS {
        int id PK
        string customer_code UK
        string first_name
        string last_name
        string email UK
        string phone
        int location_id FK
        string tier
        datetime created_at
    }

    PRODUCTS {
        int id PK
        string product_code UK
        string name
        int category_id FK
        float unit_price
        float cost_price
        string currency
        int stock_quantity
        datetime created_at
    }

    ORDERS {
        int id PK
        string order_number UK
        int customer_id FK
        datetime order_date
        string status
        float total_amount
        string currency
        float shipping_amount
        datetime created_at
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        float unit_price
        float discount
        float tax
        float item_total
    }

    BANK_ACCOUNTS {
        int id PK
        string account_number UK
        string account_type
        string customer_name
        string currency
        float balance
        string status
        datetime created_at
    }

    MERCHANTS {
        int id PK
        string merchant_name UK
        string category
        datetime created_at
    }

    TRANSACTIONS {
        int id PK
        string transaction_ref UK
        int account_id FK
        int merchant_id FK
        datetime transaction_date
        float amount
        string currency
        float amount_usd
        string transaction_type
        string category
        string description
        boolean is_expense
        boolean is_emi
        float balance_after
        datetime created_at
    }
```

---

## 2. Schema Design Rationale

### 3rd Normal Form (3NF) Compliance
- Entity attributes depend solely on their primary keys.
- Redundant data (e.g. repeated customer contact details in orders) is eliminated by referencing foreign keys.
- Product pricing and inventory reside in dimension tables, while immutable historical transaction prices are stored in order line items (`order_items.unit_price`).

### Natural Keys vs. Surrogate Keys
- **Surrogate Keys**: Integer primary keys (`id`) provide fast joins and indexing.
- **Natural Keys**: External reference codes (`customer_code`, `order_number`, `transaction_ref`, `product_code`) have unique constraints to prevent duplicate ingestion.

### Dead-Letter Queue Isolation
The `rejected_records` table captures malformed records as serialized JSON payloads (`raw_data_json`) and explicit diagnostic arrays (`rejection_reasons_json`), allowing downstream systems to audit quality without corrupting relational constraints.
