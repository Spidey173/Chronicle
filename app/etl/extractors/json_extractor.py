"""JSON data extractor."""

import json
from pathlib import Path
from typing import Any, Union
import pandas as pd
from app.etl.extractors.base import BaseExtractor
from app.utils.logger import logger


class JSONExtractor(BaseExtractor):
    """Extracts data from JSON files, raw JSON strings, or bytes."""

    def extract(self, source: Union[str, Path, bytes, dict, list], **kwargs) -> pd.DataFrame:
        try:
            records = []
            if isinstance(source, (str, Path)) and Path(str(source)).exists():
                with open(source, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif isinstance(source, (str, bytes)):
                data = json.loads(source)
            else:
                data = source

            if isinstance(data, dict):
                # Check for common container keys like "data", "records", "items"
                for key in ["data", "records", "items", "results"]:
                    if key in data and isinstance(data[key], list):
                        records = data[key]
                        break
                if not records:
                    records = [data]
            elif isinstance(data, list):
                records = data
            else:
                raise ValueError("JSON data must be a list of objects or a dict")

            df = pd.DataFrame(records).fillna("").astype(str)
            logger.info(f"Extracted {len(df)} records from JSON source", shape=list(df.shape))
            return df
        except Exception as exc:
            logger.error(f"JSON Extraction failed: {exc}")
            raise
