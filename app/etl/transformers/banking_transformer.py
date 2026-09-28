"""Banking domain data transformer."""

import uuid
from typing import Any, Dict, Optional
import pandas as pd
from app.etl.transformers.base import BaseTransformer
from app.utils.logger import logger

BANKING_CATEGORY_MAP = {
    "food": "Dining",
    "restaurant": "Dining",
    "dining": "Dining",
    "cafe": "Dining",
    "grocery": "Groceries",
    "groceries": "Groceries",
    "supermarket": "Groceries",
    "utility": "Utilities",
    "utilities": "Utilities",
    "electric": "Utilities",
    "water": "Utilities",
    "internet": "Utilities",
    "wage": "Salary",
    "salary": "Salary",
    "payroll": "Salary",
    "income": "Salary",
    "emi": "EMI & Loans",
    "loan": "EMI & Loans",
    "mortgage": "EMI & Loans",
    "health": "Healthcare",
    "medical": "Healthcare",
    "pharmacy": "Healthcare",
    "shopping": "Shopping",
    "retail": "Shopping",
    "entertainment": "Entertainment",
    "streaming": "Entertainment",
    "travel": "Travel & Transit",
    "transit": "Travel & Transit",
    "fuel": "Travel & Transit",
    "invest": "Investments",
    "stocks": "Investments",
}


class BankingTransformer(BaseTransformer):
    """Transforms banking transactions, computes USD equivalents, flags expenses and EMIs."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # Step 1: Whitespace trimming
        df_out = self.trim_whitespace(df)

        # Step 2: Standardize date
        if "transaction_date" in df_out.columns:
            df_out["transaction_date"] = df_out["transaction_date"].apply(self.standardize_date)

        # Step 3: Normalize text
        if "merchant_name" in df_out.columns:
            df_out["merchant_name"] = df_out["merchant_name"].apply(lambda m: self.normalize_text(m, "title"))
        if "description" in df_out.columns:
            df_out["description"] = df_out["description"].apply(lambda d: self.normalize_text(d, "title"))

        # Step 4: Currency & Amounts
        if "currency" not in df_out.columns:
            df_out["currency"] = "USD"
        else:
            df_out["currency"] = df_out["currency"].fillna("USD").replace("", "USD").str.upper()

        if "amount" in df_out.columns:
            df_out["amount"] = pd.to_numeric(df_out["amount"], errors="coerce").fillna(0.0).abs()
            # Calculate amount in USD
            df_out["amount_usd"] = df_out.apply(
                lambda r: self.convert_currency(r["amount"], r["currency"], "USD"),
                axis=1,
            )

        # Step 5: Normalize transaction type & Expense flag
        if "transaction_type" in df_out.columns:
            df_out["transaction_type"] = df_out["transaction_type"].str.title()
            expense_types = {"Debit", "Withdrawal", "Payment", "Transfer Out"}
            df_out["is_expense"] = df_out["transaction_type"].apply(lambda t: t in expense_types)
        else:
            df_out["transaction_type"] = "Debit"
            df_out["is_expense"] = True

        # Step 6: Category Mapping and EMI Flagging
        def categorize_and_flag_emi(row: pd.Series) -> tuple[str, bool]:
            cat_input = str(row.get("category", "")).lower().strip()
            desc_input = str(row.get("description", "")).lower().strip()

            is_emi = (
                "emi" in cat_input
                or "loan" in cat_input
                or "mortgage" in cat_input
                or "emi" in desc_input
                or "loan" in desc_input
            )

            # Map category
            matched_cat = None
            for key, canonical in BANKING_CATEGORY_MAP.items():
                if key in cat_input or key in desc_input:
                    matched_cat = canonical
                    break

            final_category = matched_cat if matched_cat else (row.get("category", "General") or "General").title()
            if is_emi:
                final_category = "EMI & Loans"

            return final_category, is_emi

        results = df_out.apply(categorize_and_flag_emi, axis=1)
        df_out["category"] = [res[0] for res in results]
        df_out["is_emi"] = [res[1] for res in results]

        # Step 7: Reference generation if missing
        if "transaction_ref" in df_out.columns and df_out["transaction_ref"].isnull().any():
            df_out["transaction_ref"] = df_out["transaction_ref"].apply(
                lambda x: f"TXN-{uuid.uuid4().hex[:10].upper()}" if not x else x
            )

        logger.info(f"Transformed {len(df_out)} banking records successfully")
        return df_out
