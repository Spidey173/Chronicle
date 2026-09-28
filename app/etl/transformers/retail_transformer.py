"""Retail domain data transformer."""

import uuid
from typing import Dict, Optional
import pandas as pd
from app.etl.transformers.base import BaseTransformer
from app.utils.logger import logger

CATEGORY_MAPPING = {
    "electronics": "Electronics",
    "electronic": "Electronics",
    "gadgets": "Electronics",
    "computers": "Electronics",
    "phones": "Electronics",
    "apparel": "Clothing",
    "clothing": "Clothing",
    "fashion": "Clothing",
    "wear": "Clothing",
    "home & kitchen": "Home & Kitchen",
    "home": "Home & Kitchen",
    "kitchen": "Home & Kitchen",
    "appliances": "Home & Kitchen",
    "beauty": "Beauty & Health",
    "health": "Beauty & Health",
    "cosmetics": "Beauty & Health",
    "books": "Books & Stationery",
    "stationery": "Books & Stationery",
    "sports": "Sports & Outdoors",
    "outdoors": "Sports & Outdoors",
    "fitness": "Sports & Outdoors",
}


class RetailTransformer(BaseTransformer):
    """Transforms retail datasets, performs revenue calculations, currency conversions, and enrichment."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # Step 1: Trim all whitespace
        df_out = self.trim_whitespace(df)

        # Step 2: Normalize customer fields if present
        if "first_name" in df_out.columns:
            df_out["first_name"] = df_out["first_name"].apply(lambda x: self.normalize_text(x, "title"))
        if "last_name" in df_out.columns:
            df_out["last_name"] = df_out["last_name"].apply(lambda x: self.normalize_text(x, "title"))
        if "email" in df_out.columns:
            df_out["email"] = df_out["email"].apply(lambda x: self.normalize_text(x, "lower"))
        if "customer_email" in df_out.columns:
            df_out["customer_email"] = df_out["customer_email"].apply(lambda x: self.normalize_text(x, "lower"))

        # Step 3: Category mapping
        if "category" in df_out.columns:
            df_out["category"] = df_out["category"].apply(
                lambda c: CATEGORY_MAPPING.get(str(c).lower().strip(), str(c).title().strip())
            )

        # Step 4: Standardize dates
        for date_col in ["order_date", "created_at", "date"]:
            if date_col in df_out.columns:
                df_out[date_col] = df_out[date_col].apply(self.standardize_date)

        # Step 5: Convert numeric columns to float/int
        if "unit_price" in df_out.columns:
            df_out["unit_price"] = pd.to_numeric(df_out["unit_price"], errors="coerce").fillna(0.0)
        if "quantity" in df_out.columns:
            df_out["quantity"] = pd.to_numeric(df_out["quantity"], errors="coerce").fillna(1).astype(int)
        if "discount" in df_out.columns:
            df_out["discount"] = pd.to_numeric(df_out["discount"], errors="coerce").fillna(0.0)
        else:
            df_out["discount"] = 0.0
        if "tax" in df_out.columns:
            df_out["tax"] = pd.to_numeric(df_out["tax"], errors="coerce").fillna(0.0)
        else:
            df_out["tax"] = 0.0
        if "currency" not in df_out.columns:
            df_out["currency"] = "USD"
        else:
            df_out["currency"] = df_out["currency"].fillna("USD").replace("", "USD")

        # Step 6: Derived columns: subtotal, item_total, revenue calculation
        if "unit_price" in df_out.columns and "quantity" in df_out.columns:
            df_out["subtotal"] = (df_out["unit_price"] * df_out["quantity"]).round(2)
            
            # Default tax calculation if 0 (e.g. 5% tax)
            df_out["tax"] = df_out.apply(
                lambda r: round(r["subtotal"] * 0.05, 2) if r["tax"] == 0.0 else round(r["tax"], 2),
                axis=1,
            )
            df_out["item_total"] = (df_out["subtotal"] - df_out["discount"] + df_out["tax"]).round(2)
            df_out["item_total"] = df_out["item_total"].apply(lambda v: max(v, 0.0))

            # Configurable Currency Conversion to USD
            df_out["item_total_usd"] = df_out.apply(
                lambda r: self.convert_currency(r["item_total"], r["currency"], "USD"),
                axis=1,
            )

        # Step 7: Surrogate key generation if identifiers are missing
        if "order_number" in df_out.columns and df_out["order_number"].isnull().any():
            df_out["order_number"] = df_out["order_number"].apply(
                lambda x: f"ORD-{uuid.uuid4().hex[:8].upper()}" if not x else x
            )

        # Step 8: Customer Tier assignment if spending information exists
        if "total_spent" in df_out.columns:
            df_out["total_spent"] = pd.to_numeric(df_out["total_spent"], errors="coerce").fillna(0.0)
            df_out["tier"] = df_out["total_spent"].apply(self._assign_tier)
        elif "tier" not in df_out.columns and "customer_code" in df_out.columns:
            df_out["tier"] = "Bronze"

        logger.info(f"Transformed {len(df_out)} retail records successfully")
        return df_out

    @staticmethod
    def _assign_tier(spent: float) -> str:
        if spent >= 5000:
            return "Platinum"
        elif spent >= 2000:
            return "Gold"
        elif spent >= 500:
            return "Silver"
        return "Bronze"
