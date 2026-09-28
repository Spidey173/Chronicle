"""Unit tests for data extractors (CSV, Excel, JSON, REST API)."""

import io
import json
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from app.etl.extractors import get_extractor, CSVExtractor, ExcelExtractor, JSONExtractor, RestAPIExtractor


def test_get_extractor_factory():
    assert isinstance(get_extractor("csv"), CSVExtractor)
    assert isinstance(get_extractor("excel"), ExcelExtractor)
    assert isinstance(get_extractor("xlsx"), ExcelExtractor)
    assert isinstance(get_extractor("json"), JSONExtractor)
    assert isinstance(get_extractor("rest_api"), RestAPIExtractor)

    with pytest.raises(ValueError):
        get_extractor("unsupported_format")


def test_csv_extractor_from_stream():
    csv_content = io.StringIO("order_number,amount\nORD-001,100.5\nORD-002,250.0\n")
    extractor = CSVExtractor()
    df = extractor.extract(csv_content)
    assert len(df) == 2
    assert "order_number" in df.columns
    assert df.iloc[0]["order_number"] == "ORD-001"


def test_json_extractor_array():
    data = [{"id": 1, "name": "Alpha"}, {"id": 2, "name": "Beta"}]
    extractor = JSONExtractor()
    df = extractor.extract(data)
    assert len(df) == 2
    assert df.iloc[1]["name"] == "Beta"


def test_json_extractor_nested_records():
    data = {"records": [{"id": 10, "item": "Widget"}, {"id": 11, "item": "Gadget"}]}
    extractor = JSONExtractor()
    df = extractor.extract(data)
    assert len(df) == 2
    assert df.iloc[0]["item"] == "Widget"


def test_excel_extractor(tmp_path):
    excel_file = tmp_path / "test.xlsx"
    pd.DataFrame([{"sku": "SKU-1", "qty": 5}, {"sku": "SKU-2", "qty": 10}]).to_excel(excel_file, index=False)
    extractor = ExcelExtractor()
    df = extractor.extract(excel_file)
    assert len(df) == 2
    assert df.iloc[0]["sku"] == "SKU-1"


@patch("httpx.Client.get")
def test_rest_api_extractor(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = [{"product": "Cloud Service", "cost": "99.0"}]
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    extractor = RestAPIExtractor()
    df = extractor.extract("https://api.example.com/v1/services")
    assert len(df) == 1
    assert df.iloc[0]["product"] == "Cloud Service"
