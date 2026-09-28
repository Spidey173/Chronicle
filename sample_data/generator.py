"""Sample dataset generator for Retail and Banking domains.
Generates CSV, Excel (.xlsx), and JSON files with both pristine and dirty validation test batches.
"""

from datetime import datetime, timedelta
import json
from pathlib import Path
import random
import pandas as pd


def generate_all_samples():
    base_dir = Path(__file__).parent
    retail_dir = base_dir / "retail"
    banking_dir = base_dir / "banking"
    retail_dir.mkdir(parents=True, exist_ok=True)
    banking_dir.mkdir(parents=True, exist_ok=True)

    print("Generating enterprise sample datasets...")

    # ---------------------------------------------------------
    # 1. RETAIL: Customers (CSV)
    # ---------------------------------------------------------
    customers = [
        {"customer_code": "CUST-0001", "first_name": "Eleanor", "last_name": "Vance", "email": "eleanor.vance@example.com", "phone": "+1-555-0192", "tier": "Platinum"},
        {"customer_code": "CUST-0002", "first_name": "Marcus", "last_name": "Chen", "email": "marcus.chen@example.com", "phone": "+1-555-0144", "tier": "Gold"},
        {"customer_code": "CUST-0003", "first_name": "Sarah", "last_name": "Connor", "email": "s.connor@example.com", "phone": "+1-555-0187", "tier": "Silver"},
        {"customer_code": "CUST-0004", "first_name": "David", "last_name": "Miller", "email": "david.m@example.com", "phone": "+1-555-0131", "tier": "Bronze"},
        {"customer_code": "CUST-0005", "first_name": "Aisha", "last_name": "Patel", "email": "aisha.patel@example.com", "phone": "+44-20-7946-0128", "tier": "Platinum"},
        {"customer_code": "CUST-0006", "first_name": "Lucas", "last_name": "Silva", "email": "lucas.silva@example.com", "phone": "+1-555-0199", "tier": "Gold"},
        {"customer_code": "CUST-0007", "first_name": "Elena", "last_name": "Rostova", "email": "elena.r@example.com", "phone": "+49-30-123456", "tier": "Silver"},
        {"customer_code": "CUST-0008", "first_name": "James", "last_name": "Wilson", "email": "j.wilson@example.com", "phone": "+1-555-0123", "tier": "Bronze"},
    ]
    pd.DataFrame(customers).to_csv(retail_dir / "customers.csv", index=False)
    print("  ✓ Created sample_data/retail/customers.csv")

    # ---------------------------------------------------------
    # 2. RETAIL: Products Catalog (JSON)
    # ---------------------------------------------------------
    products = [
        {"product_code": "PRD-TECH-01", "name": "UltraBook Pro 15", "category": "Electronics", "unit_price": 1299.99, "cost_price": 850.00, "currency": "USD", "stock_quantity": 45},
        {"product_code": "PRD-TECH-02", "name": "Noise Cancelling Headphones", "category": "Electronics", "unit_price": 249.50, "cost_price": 120.00, "currency": "USD", "stock_quantity": 120},
        {"product_code": "PRD-TECH-03", "name": "Smart Fitness Watch S3", "category": "Electronics", "unit_price": 199.00, "cost_price": 95.00, "currency": "USD", "stock_quantity": 80},
        {"product_code": "PRD-HOME-01", "name": "Espresso Barista Master", "category": "Home & Kitchen", "unit_price": 450.00, "cost_price": 220.00, "currency": "USD", "stock_quantity": 30},
        {"product_code": "PRD-HOME-02", "name": "Robot Vacuum & Mop", "category": "Home & Kitchen", "unit_price": 380.00, "cost_price": 200.00, "currency": "USD", "stock_quantity": 60},
        {"product_code": "PRD-CLOTH-01", "name": "Merino Wool Thermal Sweater", "category": "Clothing", "unit_price": 89.00, "cost_price": 35.00, "currency": "USD", "stock_quantity": 150},
        {"product_code": "PRD-CLOTH-02", "name": "Waterproof Trail Jacket", "category": "Clothing", "unit_price": 145.00, "cost_price": 60.00, "currency": "USD", "stock_quantity": 90},
        {"product_code": "PRD-BOOK-01", "name": "Designing Data-Intensive Systems", "category": "Books & Stationery", "unit_price": 49.99, "cost_price": 25.00, "currency": "USD", "stock_quantity": 200},
    ]
    with open(retail_dir / "products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)
    print("  ✓ Created sample_data/retail/products.json")

    # ---------------------------------------------------------
    # 3. RETAIL: Orders & Items (Excel .xlsx)
    # ---------------------------------------------------------
    orders_excel_data = [
        {"order_number": "ORD-2026-001", "customer_email": "eleanor.vance@example.com", "product_code": "PRD-TECH-01", "product_name": "UltraBook Pro 15", "category": "Electronics", "order_date": "2026-01-15 10:30:00", "quantity": 1, "unit_price": 1299.99, "discount": 50.0, "tax": 62.50, "currency": "USD"},
        {"order_number": "ORD-2026-001", "customer_email": "eleanor.vance@example.com", "product_code": "PRD-TECH-02", "product_name": "Noise Cancelling Headphones", "category": "Electronics", "order_date": "2026-01-15 10:30:00", "quantity": 1, "unit_price": 249.50, "discount": 0.0, "tax": 12.47, "currency": "USD"},
        {"order_number": "ORD-2026-002", "customer_email": "marcus.chen@example.com", "product_code": "PRD-HOME-01", "product_name": "Espresso Barista Master", "category": "Home & Kitchen", "order_date": "2026-02-02 14:15:00", "quantity": 1, "unit_price": 450.00, "discount": 20.0, "tax": 21.50, "currency": "USD"},
        {"order_number": "ORD-2026-003", "customer_email": "s.connor@example.com", "product_code": "PRD-CLOTH-02", "product_name": "Waterproof Trail Jacket", "category": "Clothing", "order_date": "2026-02-18 16:45:00", "quantity": 2, "unit_price": 145.00, "discount": 15.0, "tax": 13.75, "currency": "USD"},
        {"order_number": "ORD-2026-004", "customer_email": "aisha.patel@example.com", "product_code": "PRD-TECH-01", "product_name": "UltraBook Pro 15", "category": "Electronics", "order_date": "2026-03-05 09:20:00", "quantity": 2, "unit_price": 1299.99, "discount": 100.0, "tax": 124.99, "currency": "GBP"},
        {"order_number": "ORD-2026-005", "customer_email": "david.m@example.com", "product_code": "PRD-BOOK-01", "product_name": "Designing Data-Intensive Systems", "category": "Books & Stationery", "order_date": "2026-03-12 11:10:00", "quantity": 3, "unit_price": 49.99, "discount": 0.0, "tax": 7.50, "currency": "USD"},
    ]
    pd.DataFrame(orders_excel_data).to_excel(retail_dir / "orders.xlsx", index=False)
    print("  ✓ Created sample_data/retail/orders.xlsx")

    # ---------------------------------------------------------
    # 4. RETAIL: Clean Sales Transactions (CSV)
    # ---------------------------------------------------------
    sales_transactions = [
        {"order_number": "ORD-2026-101", "customer_email": "eleanor.vance@example.com", "product_code": "PRD-TECH-03", "product_name": "Smart Fitness Watch S3", "category": "Electronics", "order_date": "2026-04-10", "quantity": 1, "unit_price": 199.00, "discount": 10.0, "tax": 9.45, "currency": "USD"},
        {"order_number": "ORD-2026-102", "customer_email": "lucas.silva@example.com", "product_code": "PRD-HOME-02", "product_name": "Robot Vacuum & Mop", "category": "Home & Kitchen", "order_date": "2026-04-14", "quantity": 1, "unit_price": 380.00, "discount": 25.0, "tax": 17.75, "currency": "USD"},
        {"order_number": "ORD-2026-103", "customer_email": "elena.r@example.com", "product_code": "PRD-CLOTH-01", "product_name": "Merino Wool Thermal Sweater", "category": "Clothing", "order_date": "2026-05-01", "quantity": 2, "unit_price": 89.00, "discount": 0.0, "tax": 8.90, "currency": "EUR"},
        {"order_number": "ORD-2026-104", "customer_email": "j.wilson@example.com", "product_code": "PRD-TECH-02", "product_name": "Noise Cancelling Headphones", "category": "Electronics", "order_date": "2026-05-20", "quantity": 1, "unit_price": 249.50, "discount": 15.0, "tax": 11.72, "currency": "CAD"},
        {"order_number": "ORD-2026-105", "customer_email": "aisha.patel@example.com", "product_code": "PRD-TECH-01", "product_name": "UltraBook Pro 15", "category": "Electronics", "order_date": "2026-06-08", "quantity": 1, "unit_price": 1299.99, "discount": 50.0, "tax": 62.50, "currency": "USD"},
        {"order_number": "ORD-2026-106", "customer_email": "marcus.chen@example.com", "product_code": "PRD-BOOK-01", "product_name": "Designing Data-Intensive Systems", "category": "Books & Stationery", "order_date": "2026-06-18", "quantity": 1, "unit_price": 49.99, "discount": 0.0, "tax": 2.50, "currency": "USD"},
    ]
    pd.DataFrame(sales_transactions).to_csv(retail_dir / "retail_sales.csv", index=False)
    print("  ✓ Created sample_data/retail/retail_sales.csv")

    # ---------------------------------------------------------
    # 5. RETAIL: Dirty Batch for Data Quality & Dead-Letter Quarantine Testing
    # ---------------------------------------------------------
    retail_dirty_batch = [
        # Valid baseline record
        {"order_number": "ORD-ERR-001", "customer_email": "valid.customer@example.com", "product_code": "PRD-TECH-01", "order_date": "2026-07-01", "quantity": 1, "unit_price": 1299.99, "currency": "USD"},
        # Error 1: Missing customer_email
        {"order_number": "ORD-ERR-002", "customer_email": "", "product_code": "PRD-TECH-02", "order_date": "2026-07-02", "quantity": 1, "unit_price": 249.50, "currency": "USD"},
        # Error 2: Invalid Email format
        {"order_number": "ORD-ERR-003", "customer_email": "not-an-email-at-all", "product_code": "PRD-TECH-03", "order_date": "2026-07-03", "quantity": 1, "unit_price": 199.00, "currency": "USD"},
        # Error 3: Duplicate Record (same order_number + product_code as above)
        {"order_number": "ORD-ERR-001", "customer_email": "valid.customer@example.com", "product_code": "PRD-TECH-01", "order_date": "2026-07-01", "quantity": 1, "unit_price": 1299.99, "currency": "USD"},
        # Error 4: Invalid Date format
        {"order_number": "ORD-ERR-004", "customer_email": "date.err@example.com", "product_code": "PRD-HOME-01", "order_date": "invalid-date-9999", "quantity": 1, "unit_price": 450.00, "currency": "USD"},
        # Error 5: Negative Unit Price
        {"order_number": "ORD-ERR-005", "customer_email": "price.err@example.com", "product_code": "PRD-CLOTH-01", "order_date": "2026-07-05", "quantity": 1, "unit_price": -89.00, "currency": "USD"},
        # Error 6: Negative/Zero Quantity
        {"order_number": "ORD-ERR-006", "customer_email": "qty.err@example.com", "product_code": "PRD-BOOK-01", "order_date": "2026-07-06", "quantity": 0, "unit_price": 49.99, "currency": "USD"},
        # Error 7: Missing Product Code
        {"order_number": "ORD-ERR-007", "customer_email": "missing.prod@example.com", "product_code": "", "order_date": "2026-07-07", "quantity": 1, "unit_price": 100.00, "currency": "USD"},
    ]
    pd.DataFrame(retail_dirty_batch).to_csv(retail_dir / "retail_dirty_batch.csv", index=False)
    print("  ✓ Created sample_data/retail/retail_dirty_batch.csv (Quarantine Test Suite)")

    # ---------------------------------------------------------
    # 6. BANKING: Accounts Dimension (JSON)
    # ---------------------------------------------------------
    accounts = [
        {"account_number": "ACC-CHK-9021", "account_type": "Checking", "customer_name": "Eleanor Vance", "currency": "USD", "balance": 18450.00},
        {"account_number": "ACC-SAV-4412", "account_type": "Savings", "customer_name": "Marcus Chen", "currency": "USD", "balance": 42300.50},
        {"account_number": "ACC-LN-8831", "account_type": "Loan", "customer_name": "David Miller", "currency": "USD", "balance": 250000.00},
        {"account_number": "ACC-CHK-7719", "account_type": "Checking", "customer_name": "Aisha Patel", "currency": "GBP", "balance": 31200.00},
    ]
    with open(banking_dir / "accounts.json", "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2)
    print("  ✓ Created sample_data/banking/accounts.json")

    # ---------------------------------------------------------
    # 7. BANKING: Transactions Fact (CSV)
    # ---------------------------------------------------------
    transactions = [
        {"transaction_ref": "TXN-2026-001", "account_number": "ACC-CHK-9021", "merchant_name": "Tech Corp Payroll", "transaction_date": "2026-01-01 09:00:00", "amount": 8500.00, "currency": "USD", "transaction_type": "Credit", "category": "Salary", "description": "Bi-weekly direct deposit"},
        {"transaction_ref": "TXN-2026-002", "account_number": "ACC-CHK-9021", "merchant_name": "Whole Foods Market", "transaction_date": "2026-01-03 15:30:00", "amount": 184.20, "currency": "USD", "transaction_type": "Debit", "category": "Groceries", "description": "Weekly organic groceries"},
        {"transaction_ref": "TXN-2026-003", "account_number": "ACC-CHK-9021", "merchant_name": "First Horizon Mortgage", "transaction_date": "2026-01-05 08:00:00", "amount": 2100.00, "currency": "USD", "transaction_type": "Debit", "category": "EMI & Loans", "description": "Home Loan EMI payment"},
        {"transaction_ref": "TXN-2026-004", "account_number": "ACC-CHK-9021", "merchant_name": "ConEdison Power", "transaction_date": "2026-01-12 11:45:00", "amount": 145.80, "currency": "USD", "transaction_type": "Debit", "category": "Utilities", "description": "Electricity and heating"},
        {"transaction_ref": "TXN-2026-005", "account_number": "ACC-CHK-9021", "merchant_name": "Le Bernardin", "transaction_date": "2026-01-18 20:15:00", "amount": 320.00, "currency": "USD", "transaction_type": "Debit", "category": "Dining", "description": "Dinner with clients"},
        {"transaction_ref": "TXN-2026-006", "account_number": "ACC-CHK-9021", "merchant_name": "Tech Corp Payroll", "transaction_date": "2026-01-15 09:00:00", "amount": 8500.00, "currency": "USD", "transaction_type": "Credit", "category": "Salary", "description": "Bi-weekly direct deposit"},
        {"transaction_ref": "TXN-2026-007", "account_number": "ACC-SAV-4412", "merchant_name": "Apex Auto Finance", "transaction_date": "2026-01-20 10:00:00", "amount": 550.00, "currency": "USD", "transaction_type": "Debit", "category": "EMI & Loans", "description": "Car Loan Monthly EMI"},
        {"transaction_ref": "TXN-2026-008", "account_number": "ACC-SAV-4412", "merchant_name": "Vanguard Index Fund", "transaction_date": "2026-01-25 14:00:00", "amount": 1500.00, "currency": "USD", "transaction_type": "Debit", "category": "Investments", "description": "Automatic index investment"},
        {"transaction_ref": "TXN-2026-009", "account_number": "ACC-CHK-7719", "merchant_name": "London Fintech Ltd", "transaction_date": "2026-01-28 09:30:00", "amount": 6200.00, "currency": "GBP", "transaction_type": "Credit", "category": "Salary", "description": "Monthly executive retainer"},
    ]
    pd.DataFrame(transactions).to_csv(banking_dir / "transactions.csv", index=False)
    print("  ✓ Created sample_data/banking/transactions.csv")

    # ---------------------------------------------------------
    # 8. BANKING: Dirty Batch for Banking Dead-Letter Quarantine Testing
    # ---------------------------------------------------------
    banking_dirty_batch = [
        {"transaction_ref": "TXN-ERR-001", "account_number": "ACC-CHK-9021", "transaction_date": "2026-02-01", "amount": 100.0, "transaction_type": "Debit", "category": "Dining"},
        # Error 1: Missing Transaction Ref
        {"transaction_ref": "", "account_number": "ACC-CHK-9021", "transaction_date": "2026-02-02", "amount": 50.0, "transaction_type": "Debit", "category": "Groceries"},
        # Error 2: Missing Account Number
        {"transaction_ref": "TXN-ERR-002", "account_number": "", "transaction_date": "2026-02-03", "amount": 75.0, "transaction_type": "Debit", "category": "Utilities"},
        # Error 3: Duplicate Transaction Ref
        {"transaction_ref": "TXN-ERR-001", "account_number": "ACC-CHK-9021", "transaction_date": "2026-02-01", "amount": 100.0, "transaction_type": "Debit", "category": "Dining"},
        # Error 4: Invalid Date
        {"transaction_ref": "TXN-ERR-003", "account_number": "ACC-CHK-9021", "transaction_date": "corrupted-date", "amount": 80.0, "transaction_type": "Debit", "category": "Shopping"},
        # Error 5: Negative/Zero Amount
        {"transaction_ref": "TXN-ERR-004", "account_number": "ACC-CHK-9021", "transaction_date": "2026-02-04", "amount": -150.0, "transaction_type": "Debit", "category": "Dining"},
        # Error 6: Invalid Transaction Type
        {"transaction_ref": "TXN-ERR-005", "account_number": "ACC-CHK-9021", "transaction_date": "2026-02-05", "amount": 200.0, "transaction_type": "IllegalType", "category": "Dining"},
    ]
    pd.DataFrame(banking_dirty_batch).to_csv(banking_dir / "banking_dirty_batch.csv", index=False)
    print("  ✓ Created sample_data/banking/banking_dirty_batch.csv (Quarantine Test Suite)")

    print("\nAll sample datasets generated successfully!")


if __name__ == "__main__":
    generate_all_samples()
