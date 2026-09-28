"""CSV data extractor."""

import io
from pathlib import Path
from typing import Any, Union
import pandas as pd
from app.etl.extractors.base import BaseExtractor
from app.utils.logger import logger


class CSVExtractor(BaseExtractor):
    """Extracts tabular data from CSV files or byte streams."""

    def extract(self, source: Union[str, Path, io.BytesIO], **kwargs) -> pd.DataFrame:
        encoding = kwargs.get("encoding", "utf-8")
        delimiter = kwargs.get("delimiter", ",")

        try:
            if isinstance(source, (str, Path)):
                path_obj = Path(source)
                if not path_obj.exists():
                    raise FileNotFoundError(f"CSV source file not found at: {source}")
                df = pd.read_csv(source, encoding=encoding, sep=delimiter, dtype=str)
            else:
                # Handle bytes / StringIO
                df = pd.read_csv(source, encoding=encoding, sep=delimiter, dtype=str)

            # Fill NA with empty string for uniform string processing
            df = df.fillna("")
            logger.info(f"Extracted {len(df)} records from CSV source", shape=list(df.shape))
            return df
        except UnicodeDecodeError:
            # Fallback encoding attempt
            logger.warning("UTF-8 decoding failed, falling back to latin1")
            if isinstance(source, (str, Path)):
                df = pd.read_csv(source, encoding="latin1", sep=delimiter, dtype=str).fillna("")
                return df
            source.seek(0)
            return pd.read_csv(source, encoding="latin1", sep=delimiter, dtype=str).fillna("")
        except Exception as exc:
            logger.error(f"CSV Extraction failed: {exc}")
            raise
