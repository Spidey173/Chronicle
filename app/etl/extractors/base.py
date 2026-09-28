"""Base extractor interface and extractor factory."""

from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd


class BaseExtractor(ABC):
    """Abstract base class for all data extractors."""

    @abstractmethod
    def extract(self, source: Any, **kwargs) -> pd.DataFrame:
        """Extract data from the source and return a pandas DataFrame.
        
        Args:
            source: File path, file-like object, or URL endpoint.
            **kwargs: Extractor-specific configuration options.
            
        Returns:
            pd.DataFrame containing raw extracted records.
        """
        pass
