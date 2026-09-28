"""Base validator interface, validation result container, and standard rules."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Any, Dict, List, Optional
import pandas as pd
from app.utils.logger import logger

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[\d\s\-().]{7,25}$")


@dataclass
class RejectedItem:
    record_index: int
    raw_data: Dict[str, Any]
    reasons: List[str]


@dataclass
class ValidationResult:
    valid_df: pd.DataFrame
    rejected_items: List[RejectedItem] = field(default_factory=list)
    total_input: int = 0
    valid_count: int = 0
    rejected_count: int = 0
    rule_counts: Dict[str, int] = field(default_factory=dict)


class BaseValidator(ABC):
    """Abstract base validator providing core validation primitives."""

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """Validate input DataFrame and partition into valid and rejected records."""
        pass

    def check_email(self, email: str) -> bool:
        """Check if an email string is well-formed."""
        if not email or not isinstance(email, str):
            return False
        clean = email.strip()
        return bool(EMAIL_REGEX.match(clean))

    def check_phone(self, phone: str) -> bool:
        """Check if a phone number matches standard international or local patterns."""
        if not phone or not isinstance(phone, str):
            return False
        clean = phone.strip()
        # Ensure it has at least 7 digits
        digits = re.sub(r"\D", "", clean)
        return bool(PHONE_REGEX.match(clean)) and (7 <= len(digits) <= 15)

    def check_date(self, date_str: str) -> bool:
        """Check if a date string is parseable into a valid date."""
        if not date_str or not isinstance(date_str, str):
            return False
        clean = date_str.strip()
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%d/%m/%Y",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(clean, fmt)
                # Ensure date is within reasonable bounds (1970 to 2100)
                if 1970 <= dt.year <= 2100:
                    return True
            except ValueError:
                continue
        return False

    def check_numeric(
        self,
        value: Any,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        allow_zero: bool = True,
    ) -> bool:
        """Validate if a value is numeric and within optional bounds."""
        if value is None or value == "":
            return False
        try:
            val_float = float(value)
            if not allow_zero and val_float == 0.0:
                return False
            if min_val is not None and val_float < min_val:
                return False
            if max_val is not None and val_float > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False
