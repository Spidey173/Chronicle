"""Validators factory and registry."""

from typing import Dict, Type
from app.etl.validators.base import BaseValidator, RejectedItem, ValidationResult
from app.etl.validators.retail_validator import RetailValidator
from app.etl.validators.banking_validator import BankingValidator

_VALIDATORS: Dict[str, Type[BaseValidator]] = {
    "retail": RetailValidator,
    "ecommerce": RetailValidator,
    "sales": RetailValidator,
    "customer": RetailValidator,
    "banking": BankingValidator,
    "finance": BankingValidator,
}


def get_validator(domain: str) -> BaseValidator:
    """Factory to retrieve domain-specific validator."""
    normalized = domain.lower().strip()
    val_cls = _VALIDATORS.get(normalized)
    if not val_cls:
        valid_domains = ", ".join(set(_VALIDATORS.keys()))
        raise ValueError(f"No validator for domain '{domain}'. Supported domains: {valid_domains}")
    return val_cls()


__all__ = [
    "BaseValidator",
    "RejectedItem",
    "ValidationResult",
    "RetailValidator",
    "BankingValidator",
    "get_validator",
]
