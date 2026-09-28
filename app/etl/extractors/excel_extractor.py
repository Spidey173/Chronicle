"""Excel data extractor (.xlsx, .xls)."""

import io
from pathlib import Path
from typing import Any, Union
import pandas as pd
from app.etl.extractors.base import BaseExtractor
from app.utils.logger import logger


class ExcelExtractor(BaseExtractor):
    """Extracts tabular data from Microsoft Excel spreadsheets."""

    def extract(self, source: Union[str, Path, io.BytesIO], **kwargs) -> pd.DataFrame:
        sheet_name = kwargs.get("sheet_name", 0)

        try:
            if isinstance(source, (str, Path)):
                path_obj = Path(source)
                if not path_obj.exists():
                    raise FileNotFoundError(f"Excel source file not found at: {source}")
            
            df = pd.read_excel(source, sheet_name=sheet_name, dtype=str)
            df = df.fillna("")
            logger.info(f"Extracted {len(df)} records from Excel spreadsheet", shape=list(df.shape))
            return df
        except Exception as exc:
            logger.error(f"Excel Extraction failed: {exc}")
            raise
