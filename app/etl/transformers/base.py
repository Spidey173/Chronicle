"""Base transformer interface and shared transformation primitives."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
import pandas as pd
from dateutil import parser
from app.config import settings
from app.utils.logger import logger


class BaseTransformer(ABC):
    """Abstract base transformer with common data cleansing and enrichment functions."""

    def __init__(self, exchange_rates: Optional[Dict[str, float]] = None):
        self.exchange_rates = exchange_rates or settings.currency_rates

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform clean DataFrame and calculate derived metrics."""
        pass

    def trim_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        """Strip leading/trailing whitespaces from all string columns."""
        df_out = df.copy()
        for col in df_out.columns:
            if df_out[col].dtype == object or isinstance(df_out[col].iloc[0] if len(df_out) > 0 else None, str):
                df_out[col] = df_out[col].astype(str).str.strip()
        return df_out

    def standardize_date(self, val: Any) -> Optional[datetime]:
        """Convert arbitrary date representations into datetime object."""
        if val is None or val == "" or pd.isna(val):
            return None
        if isinstance(val, datetime):
            return val
        try:
            return parser.parse(str(val).strip())
        except Exception:
            return None

    def convert_currency(self, amount: float, from_curr: str, to_curr: str = "USD") -> float:
        """Convert an amount from a given currency to a target currency (default USD)."""
        from_rate = self.exchange_rates.get(from_curr.upper(), 1.0)
        to_rate = self.exchange_rates.get(to_curr.upper(), 1.0)

        # Convert to USD first, then to target
        amount_in_usd = amount * from_rate
        if to_curr.upper() == "USD":
            return round(amount_in_usd, 2)
        return round(amount_in_usd / to_rate, 2)

    def normalize_text(self, val: Any, case: str = "title") -> str:
        """Clean and normalize text fields."""
        if val is None or pd.isna(val):
            return ""
        text = str(val).strip()
        if case == "lower":
            return text.lower()
        elif case == "upper":
            return text.upper()
        elif case == "title":
            return text.title()
        return text
