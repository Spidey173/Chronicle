"""Unit tests for data transformers (derived calculations, currency conversions, mapping)."""

import pandas as pd
from app.etl.transformers import get_transformer, RetailTransformer, BankingTransformer


def test_retail_transformer_derived_columns():
    df = pd.DataFrame([
        {
            "order_number": "ORD-501",
            "customer_email": "ALICE@EXAMPLE.COM  ",
            "first_name": "  alice ",
            "last_name": "smith ",
            "product_code": "PRD-X",
            "category": "electronics",
            "order_date": "2026-06-15",
            "unit_price": "100.0",
            "quantity": "2",
            "discount": "10.0",
            "tax": "15.0",
            "currency": "EUR",
        }
    ])
    transformer = RetailTransformer(exchange_rates={"USD": 1.0, "EUR": 1.10})
    out = transformer.transform(df)

    assert out.iloc[0]["first_name"] == "Alice"
    assert out.iloc[0]["last_name"] == "Smith"
    assert out.iloc[0]["customer_email"] == "alice@example.com"
    assert out.iloc[0]["category"] == "Electronics"  # Mapped
    assert out.iloc[0]["subtotal"] == 200.0  # 100 * 2
    assert out.iloc[0]["item_total"] == 205.0  # 200 - 10 + 15
    # Currency conversion: 205 * 1.10 = 225.50
    assert out.iloc[0]["item_total_usd"] == 225.50


def test_customer_tier_enrichment():
    df = pd.DataFrame([
        {"customer_code": "C1", "total_spent": 6000},
        {"customer_code": "C2", "total_spent": 3000},
        {"customer_code": "C3", "total_spent": 800},
        {"customer_code": "C4", "total_spent": 100},
    ])
    transformer = RetailTransformer()
    out = transformer.transform(df)

    assert out.iloc[0]["tier"] == "Platinum"
    assert out.iloc[1]["tier"] == "Gold"
    assert out.iloc[2]["tier"] == "Silver"
    assert out.iloc[3]["tier"] == "Bronze"


def test_banking_transformer():
    df = pd.DataFrame([
        {
            "transaction_ref": "TX-99",
            "account_number": "ACC-100",
            "amount": "1500.00",
            "currency": "GBP",
            "transaction_type": "debit",
            "category": "home mortgage loan emi",
            "description": "monthly home loan payment",
        },
        {
            "transaction_ref": "TX-100",
            "account_number": "ACC-100",
            "amount": "5000.00",
            "currency": "USD",
            "transaction_type": "credit",
            "category": "payroll salary",
            "description": "monthly direct deposit",
        },
    ])
    transformer = BankingTransformer(exchange_rates={"USD": 1.0, "GBP": 1.30})
    out = transformer.transform(df)

    # First txn
    assert bool(out.iloc[0]["is_expense"]) is True
    assert bool(out.iloc[0]["is_emi"]) is True
    assert out.iloc[0]["category"] == "EMI & Loans"
    assert out.iloc[0]["amount_usd"] == 1950.0  # 1500 * 1.30

    # Second txn
    assert bool(out.iloc[1]["is_expense"]) is False
    assert bool(out.iloc[1]["is_emi"]) is False
    assert out.iloc[1]["category"] == "Salary"
    assert out.iloc[1]["amount_usd"] == 5000.0
