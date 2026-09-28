"""Extractors module factory and registry."""

from typing import Dict, Type
from app.etl.extractors.base import BaseExtractor
from app.etl.extractors.csv_extractor import CSVExtractor
from app.etl.extractors.excel_extractor import ExcelExtractor
from app.etl.extractors.json_extractor import JSONExtractor
from app.etl.extractors.rest_api_extractor import RestAPIExtractor

_EXTRACTORS: Dict[str, Type[BaseExtractor]] = {
    "csv": CSVExtractor,
    "excel": ExcelExtractor,
    "xlsx": ExcelExtractor,
    "xls": ExcelExtractor,
    "json": JSONExtractor,
    "rest_api": RestAPIExtractor,
    "api": RestAPIExtractor,
}


def get_extractor(source_type: str) -> BaseExtractor:
    """Factory to retrieve the appropriate extractor instance."""
    normalized_type = source_type.lower().strip()
    extractor_cls = _EXTRACTORS.get(normalized_type)
    if not extractor_cls:
        valid_types = ", ".join(_EXTRACTORS.keys())
        raise ValueError(f"Unsupported source type '{source_type}'. Supported types: {valid_types}")
    return extractor_cls()


__all__ = [
    "BaseExtractor",
    "CSVExtractor",
    "ExcelExtractor",
    "JSONExtractor",
    "RestAPIExtractor",
    "get_extractor",
]
