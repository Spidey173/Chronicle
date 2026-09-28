"""Base loader interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import pandas as pd
from sqlalchemy.orm import Session
from app.etl.validators.base import RejectedItem


class BaseLoader(ABC):
    """Abstract base loader for persisting transformed data into relational store."""

    @abstractmethod
    def load(
        self,
        df: pd.DataFrame,
        batch_id: str,
        rejected_items: List[RejectedItem],
        db: Session,
        **kwargs,
    ) -> Dict[str, Any]:
        """Load valid DataFrame records and rejected records into database.
        
        Args:
            df: Transformed valid records.
            batch_id: Unique execution batch UUID.
            rejected_items: Records that failed validation.
            db: Active SQLAlchemy Session.
            
        Returns:
            Dict containing insertion counts and summary details.
        """
        pass
