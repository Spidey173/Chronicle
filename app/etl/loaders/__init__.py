"""Loaders module factory and registry."""

from typing import Dict
from app.etl.loaders.base import BaseLoader
from app.etl.loaders.postgres_loader import RelationalLoader


def get_loader(domain: str) -> BaseLoader:
    """Factory to retrieve loader for domain."""
    return RelationalLoader(domain=domain)


__all__ = ["BaseLoader", "RelationalLoader", "get_loader"]
