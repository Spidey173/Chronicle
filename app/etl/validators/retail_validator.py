"""Retail domain data validator."""

from collections import defaultdict
from typing import Dict, List, Set
import pandas as pd
from app.etl.validators.base import BaseValidator, RejectedItem, ValidationResult
from app.utils.logger import logger


class RetailValidator(BaseValidator):
    """Validates retail datasets including customers, products, orders, and sales batches."""

    REQUIRED_COLUMNS_BY_ENTITY = {
        "customers": ["customer_code", "first_name", "last_name", "email"],
        "products": ["product_code", "name", "category", "unit_price"],
        "orders": ["order_number", "customer_email", "order_date", "total_amount"],
        "order_items": ["order_number", "product_code", "quantity", "unit_price"],
        "retail_sales": ["order_number", "customer_email", "product_code", "order_date", "quantity", "unit_price"],
    }

    def detect_entity_type(self, columns: List[str]) -> str:
        """Infer entity type based on column names."""
        cols_lower = [c.lower().strip() for c in columns]
        if "product_code" in cols_lower and "quantity" in cols_lower and "customer_email" in cols_lower:
            return "retail_sales"
        if "customer_code" in cols_lower and "email" in cols_lower:
            return "customers"
        if "product_code" in cols_lower and "unit_price" in cols_lower and "quantity" not in cols_lower:
            return "products"
        if "order_number" in cols_lower and "total_amount" in cols_lower:
            return "orders"
        return "retail_sales"

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        if df.empty:
            return ValidationResult(valid_df=df, total_input=0, valid_count=0, rejected_count=0)

        # Standardize column headers (lowercase, trimmed)
        df_clean = df.copy()
        df_clean.columns = [str(c).lower().strip().replace(" ", "_") for c in df_clean.columns]

        entity_type = self.detect_entity_type(list(df_clean.columns))
        required_cols = self.REQUIRED_COLUMNS_BY_ENTITY.get(entity_type, [])

        # Schema Mismatch Check
        missing_schema_cols = [c for c in required_cols if c not in df_clean.columns]
        if missing_schema_cols:
            logger.error("Schema mismatch detected", missing_columns=missing_schema_cols)
            # All records rejected due to missing schema
            rejected_items = [
                RejectedItem(
                    record_index=idx,
                    raw_data=row.to_dict(),
                    reasons=[f"Schema mismatch: missing required columns {missing_schema_cols}"],
                )
                for idx, row in df_clean.iterrows()
            ]
            return ValidationResult(
                valid_df=pd.DataFrame(),
                rejected_items=rejected_items,
                total_input=len(df),
                valid_count=0,
                rejected_count=len(df),
                rule_counts={"schema_mismatch": len(df)},
            )

        valid_rows = []
        rejected_items: List[RejectedItem] = []
        rule_counts: Dict[str, int] = defaultdict(int)
        seen_keys: Set[str] = set()

        for idx, row in df_clean.iterrows():
            reasons: List[str] = []
            row_dict = row.to_dict()

            # 1. Check Missing Values for required columns
            for col in required_cols:
                val = str(row_dict.get(col, "")).strip()
                if not val:
                    reasons.append(f"Missing required value for column: '{col}'")
                    rule_counts["missing_values"] += 1

            # 2. Check Duplicates based on primary key / business key
            if "customer_code" in df_clean.columns:
                key = f"cust_{row_dict.get('customer_code', '').strip()}"
            elif "order_number" in df_clean.columns and "product_code" in df_clean.columns:
                key = f"order_item_{row_dict.get('order_number', '').strip()}_{row_dict.get('product_code', '').strip()}"
            elif "order_number" in df_clean.columns:
                key = f"order_{row_dict.get('order_number', '').strip()}"
            elif "product_code" in df_clean.columns:
                key = f"prod_{row_dict.get('product_code', '').strip()}"
            else:
                key = str(idx)

            if key in seen_keys:
                reasons.append(f"Duplicate record detected for key: '{key}'")
                rule_counts["duplicate_records"] += 1
            else:
                seen_keys.add(key)

            # 3. Check Email format if present
            for email_col in ["email", "customer_email"]:
                if email_col in df_clean.columns:
                    email_val = str(row_dict.get(email_col, "")).strip()
                    if email_val and not self.check_email(email_val):
                        reasons.append(f"Invalid email address: '{email_val}'")
                        rule_counts["invalid_email"] += 1

            # 4. Check Phone format if present
            if "phone" in df_clean.columns:
                phone_val = str(row_dict.get("phone", "")).strip()
                if phone_val and not self.check_phone(phone_val):
                    reasons.append(f"Invalid phone number: '{phone_val}'")
                    rule_counts["invalid_phone"] += 1

            # 5. Check Dates if present
            for date_col in ["order_date", "created_at", "date"]:
                if date_col in df_clean.columns:
                    date_val = str(row_dict.get(date_col, "")).strip()
                    if date_val and not self.check_date(date_val):
                        reasons.append(f"Invalid date format in '{date_col}': '{date_val}'")
                        rule_counts["invalid_dates"] += 1

            # 6. Check Numeric values (Prices, Quantities, Amounts)
            for num_col in ["unit_price", "cost_price", "total_amount", "amount"]:
                if num_col in df_clean.columns:
                    num_val = row_dict.get(num_col, "")
                    if str(num_val).strip() != "" and not self.check_numeric(num_val, min_val=0.0):
                        reasons.append(f"Incorrect numeric value for '{num_col}': '{num_val}' (must be >= 0)")
                        rule_counts["incorrect_numeric"] += 1

            for qty_col in ["quantity", "stock_quantity"]:
                if qty_col in df_clean.columns:
                    qty_val = row_dict.get(qty_col, "")
                    if str(qty_val).strip() != "" and not self.check_numeric(qty_val, min_val=1.0 if qty_col == "quantity" else 0.0):
                        reasons.append(f"Incorrect numeric value for '{qty_col}': '{qty_val}' (must be positive integer)")
                        rule_counts["incorrect_numeric"] += 1

            if reasons:
                rejected_items.append(
                    RejectedItem(record_index=int(idx), raw_data=row.to_dict(), reasons=reasons)
                )
            else:
                valid_rows.append(row)

        valid_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame(columns=df_clean.columns)
        return ValidationResult(
            valid_df=valid_df,
            rejected_items=rejected_items,
            total_input=len(df),
            valid_count=len(valid_df),
            rejected_count=len(rejected_items),
            rule_counts=dict(rule_counts),
        )
