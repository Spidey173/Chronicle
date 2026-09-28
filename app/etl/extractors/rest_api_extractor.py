"""REST API data extractor."""

from typing import Any, Dict, Optional
import httpx
import pandas as pd
from app.etl.extractors.base import BaseExtractor
from app.etl.extractors.json_extractor import JSONExtractor
from app.utils.logger import logger


class RestAPIExtractor(BaseExtractor):
    """Extracts data from external REST API endpoints."""

    def extract(self, source: str, **kwargs) -> pd.DataFrame:
        """Fetch records from a REST API endpoint.
        
        Args:
            source: HTTP or HTTPS URL to the endpoint.
            **kwargs:
                headers: Dict[str, str] of request headers (e.g. Authorization)
                params: Dict[str, Any] of query parameters
                timeout: Request timeout in seconds (default 30)
                json_path: Optional key to extract list from (e.g. "data")
        """
        headers: Dict[str, str] = kwargs.get("headers", {})
        params: Dict[str, Any] = kwargs.get("params", {})
        timeout: float = kwargs.get("timeout", 30.0)

        logger.info("Extracting data from REST API", url=source, params=params)
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(source, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

            json_extractor = JSONExtractor()
            return json_extractor.extract(data)
        except Exception as exc:
            logger.error(f"REST API Extraction failed for {source}: {exc}")
            raise
