"""Banking domain data validator."""

from collections import defaultdict
from typing import Dict, List, Set
import pandas as pd
from app.etl.validators.base import BaseValidator, RejectedItem, ValidationResult
from app.utils.logger import logger


class BankingValidator(BaseValidator):
    """Validates banking accounts and financial transaction datasets."""

    REQUIRED_TRANSACTION_COLS = ["transaction_ref", "account_number", "transaction_date", "amount", "transaction_type"]
    REQUIRED_ACCOUNT_COLS = ["account_number", "account_type", "customer_name"]
    ALLOWED_TXN_TYPES = {"credit", "debit", "deposit", "withdrawal", "transfer", "payment"}

    def detect_entity_type(self, columns: List[str]) -> str:
        cols_lower = [c.lower().strip() for c in columns]
        if "transaction_ref" in cols_lower or "amount" in cols_lower:
            return "transactions"
        if "account_number" in cols_lower and "customer_name" in cols_lower:
            return "accounts"
        return "transactions"

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        if df.empty:
            return ValidationResult(valid_df=df, total_input=0, valid_count=0, rejected_count=0)

        df_clean = df.copy()
        df_clean.columns = [str(c).lower().strip().replace(" ", "_") for c in df_clean.columns]

        entity_type = self.detect_entity_type(list(df_clean.columns))
        required_cols = self.REQUIRED_ACCOUNT_COLS if entity_type == "accounts" else self.REQUIRED_TRANSACTION_COLS

        # Schema check
        missing_cols = [c for c in required_cols if c not in df_clean.columns]
        if missing_cols:
            logger.error("Banking schema mismatch", missing_columns=missing_cols)
            rejected_items = [
                RejectedItem(
                    record_index=idx,
                    raw_data=row.to_dict(),
                    reasons=[f"Schema mismatch: missing required columns {missing_cols}"],
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

            # 1. Check Missing Values
            for col in required_cols:
                val = str(row_dict.get(col, "")).strip()
                if not val:
                    reasons.append(f"Missing required value for column: '{col}'")
                    rule_counts["missing_values"] += 1

            # 2. Check Duplicates
            if entity_type == "accounts":
                key = str(row_dict.get("account_number", "")).strip()
            else:
                key = str(row_dict.get("transaction_ref", "")).strip()

            if key in seen_keys:
                reasons.append(f"Duplicate record identifier: '{key}'")
                rule_counts["duplicate_records"] += 1
            else:
                if key:
                    seen_keys.add(key)

            # 3. Check Date (transactions only)
            if "transaction_date" in df_clean.columns:
                date_val = str(row_dict.get("transaction_date", "")).strip()
                if date_val and not self.check_date(date_val):
                    reasons.append(f"Invalid transaction date format: '{date_val}'")
                    rule_counts["invalid_dates"] += 1

            # 4. Check Amount (transactions only)
            if "amount" in df_clean.columns:
                amount_val = row_dict.get("amount", "")
                if str(amount_val).strip() != "" and not self.check_numeric(amount_val, min_val=0.01, allow_zero=False):
                    reasons.append(f"Incorrect amount: '{amount_val}' (must be positive number > 0)")
                    rule_counts["incorrect_numeric"] += 1

            # Check Balance (accounts)
            if "balance" in df_clean.columns:
                bal_val = row_dict.get("balance", "")
                if str(bal_val).strip() != "" and not self.check_numeric(bal_val):
                    reasons.append(f"Incorrect balance value: '{bal_val}'")
                    rule_counts["incorrect_numeric"] += 1

            # 5. Check Transaction Type
            if "transaction_type" in df_clean.columns:
                txn_type = str(row_dict.get("transaction_type", "")).strip().lower()
                if txn_type and txn_type not in self.ALLOWED_TXN_TYPES:
                    reasons.append(f"Invalid transaction type: '{txn_type}'. Allowed: {sorted(self.ALLOWED_TXN_TYPES)}")
                    rule_counts["invalid_transaction_type"] += 1

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
