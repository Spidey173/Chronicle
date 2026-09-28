"""Unit tests for domain validators and data quality quarantine logic."""

import pandas as pd
import pytest

from app.etl.validators import get_validator, RetailValidator, BankingValidator


def test_validator_factory():
    assert isinstance(get_validator("retail"), RetailValidator)
    assert isinstance(get_validator("banking"), BankingValidator)
    with pytest.raises(ValueError):
        get_validator("nonexistent_domain")


def test_retail_validator_clean_batch():
    df = pd.DataFrame([
        {
            "order_number": "ORD-101",
            "customer_email": "jane@example.com",
            "product_code": "PRD-A",
            "order_date": "2026-05-01",
            "quantity": 2,
            "unit_price": 50.0,
        },
        {
            "order_number": "ORD-102",
            "customer_email": "john@example.com",
            "product_code": "PRD-B",
            "order_date": "2026-05-02",
            "quantity": 1,
            "unit_price": 100.0,
        },
    ])
    validator = RetailValidator()
    result = validator.validate(df)
    assert result.total_input == 2
    assert result.valid_count == 2
    assert result.rejected_count == 0
    assert len(result.rejected_items) == 0


def test_retail_validator_quarantine_rejections():
    df = pd.DataFrame([
        # Valid
        {"order_number": "ORD-201", "customer_email": "valid@example.com", "product_code": "PRD-1", "order_date": "2026-06-01", "quantity": 1, "unit_price": 25.0},
        # Missing email
        {"order_number": "ORD-202", "customer_email": "", "product_code": "PRD-2", "order_date": "2026-06-01", "quantity": 1, "unit_price": 25.0},
        # Invalid email format
        {"order_number": "ORD-203", "customer_email": "not-an-email", "product_code": "PRD-3", "order_date": "2026-06-01", "quantity": 1, "unit_price": 25.0},
        # Negative numeric price
        {"order_number": "ORD-204", "customer_email": "valid2@example.com", "product_code": "PRD-4", "order_date": "2026-06-01", "quantity": 1, "unit_price": -50.0},
        # Zero quantity
        {"order_number": "ORD-205", "customer_email": "valid3@example.com", "product_code": "PRD-5", "order_date": "2026-06-01", "quantity": 0, "unit_price": 10.0},
        # Duplicate order item
        {"order_number": "ORD-201", "customer_email": "valid@example.com", "product_code": "PRD-1", "order_date": "2026-06-01", "quantity": 1, "unit_price": 25.0},
    ])
    validator = RetailValidator()
    result = validator.validate(df)

    assert result.total_input == 6
    assert result.valid_count == 1
    assert result.rejected_count == 5
    assert len(result.rejected_items) == 5

    # Verify error reasons exist
    all_reasons = [r for item in result.rejected_items for r in item.reasons]
    assert any("Missing required value" in r for r in all_reasons)
    assert any("Invalid email" in r for r in all_reasons)
    assert any("Incorrect numeric value" in r for r in all_reasons)
    assert any("Duplicate record" in r for r in all_reasons)


def test_banking_validator_transactions():
    df = pd.DataFrame([
        {"transaction_ref": "TX-1", "account_number": "ACC-1", "transaction_date": "2026-01-10", "amount": 100.0, "transaction_type": "Debit"},
        # Missing account number
        {"transaction_ref": "TX-2", "account_number": "", "transaction_date": "2026-01-11", "amount": 50.0, "transaction_type": "Debit"},
        # Negative amount
        {"transaction_ref": "TX-3", "account_number": "ACC-1", "transaction_date": "2026-01-12", "amount": -20.0, "transaction_type": "Debit"},
        # Invalid type
        {"transaction_ref": "TX-4", "account_number": "ACC-1", "transaction_date": "2026-01-13", "amount": 30.0, "transaction_type": "InvalidType"},
    ])
    validator = BankingValidator()
    result = validator.validate(df)

    assert result.total_input == 4
    assert result.valid_count == 1
    assert result.rejected_count == 3
