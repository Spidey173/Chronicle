"""Transformers module factory and registry."""

from typing import Dict, Type
from app.etl.transformers.base import BaseTransformer
from app.etl.transformers.retail_transformer import RetailTransformer
from app.etl.transformers.banking_transformer import BankingTransformer

_TRANSFORMERS: Dict[str, Type[BaseTransformer]] = {
    "retail": RetailTransformer,
    "ecommerce": RetailTransformer,
    "sales": RetailTransformer,
    "customer": RetailTransformer,
    "banking": BankingTransformer,
    "finance": BankingTransformer,
}


def get_transformer(domain: str) -> BaseTransformer:
    """Factory to retrieve domain-specific transformer."""
    normalized = domain.lower().strip()
    trans_cls = _TRANSFORMERS.get(normalized)
    if not trans_cls:
        valid_domains = ", ".join(set(_TRANSFORMERS.keys()))
        raise ValueError(f"No transformer for domain '{domain}'. Supported domains: {valid_domains}")
    return trans_cls()


__all__ = [
    "BaseTransformer",
    "RetailTransformer",
    "BankingTransformer",
    "get_transformer",
]
