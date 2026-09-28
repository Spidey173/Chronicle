"""Relational database loader for PostgreSQL / SQLite."""

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List
import uuid
import pandas as pd
from sqlalchemy.orm import Session

from app.etl.loaders.base import BaseLoader
from app.etl.validators.base import RejectedItem
from app.models.common import RejectedRecord
from app.models.retail import Category, Customer, Location, Order, OrderItem, Product
from app.models.banking import BankAccount, Merchant, Transaction
from app.utils.logger import logger


class RelationalLoader(BaseLoader):
    """Loads transformed records into normalized database tables and records rejections."""

    def __init__(self, domain: str = "retail"):
        self.domain = domain.lower()

    def load(
        self,
        df: pd.DataFrame,
        batch_id: str,
        rejected_items: List[RejectedItem],
        db: Session,
        **kwargs,
    ) -> Dict[str, Any]:
        source_name = kwargs.get("source_name", "unknown_source")
        summary: Dict[str, Any] = {
            "inserted_records": 0,
            "quarantined_records": len(rejected_items),
            "entities_affected": {},
        }

        try:
            # 1. Store Rejected Records in Quarantine Table
            if rejected_items:
                rejected_records_to_insert = []
                for item in rejected_items:
                    rec = RejectedRecord(
                        batch_id=batch_id,
                        domain=self.domain,
                        source_identifier=source_name,
                        record_index=item.record_index,
                    )
                    rec.set_raw_data(item.raw_data)
                    rec.set_reasons(item.reasons)
                    rejected_records_to_insert.append(rec)

                db.bulk_save_objects(rejected_records_to_insert)
                logger.log_database_insert("rejected_records", len(rejected_records_to_insert), batch_id)

            # 2. Load Valid Transformed Records
            if not df.empty:
                if self.domain in ["retail", "ecommerce", "sales"]:
                    self._load_retail(df, db, summary)
                elif self.domain in ["banking", "finance"]:
                    self._load_banking(df, db, summary)
                else:
                    logger.warning(f"No specific relational loader for domain '{self.domain}'")

            db.commit()
            return summary
        except Exception as exc:
            db.rollback()
            logger.error(f"Database loading failed for batch {batch_id}: {exc}")
            raise

    def _load_retail(self, df: pd.DataFrame, db: Session, summary: Dict[str, Any]) -> None:
        """Load retail data (customers, products, categories, orders, order items)."""
        # Cache existing dimensions
        categories = {c.name.lower(): c for c in db.query(Category).all()}
        locations = {
            f"{l.city.lower()}:{l.state.lower() if l.state else ''}:{l.country.lower()}": l
            for l in db.query(Location).all()
        }
        customers = {c.customer_code: c for c in db.query(Customer).all()}
        customers_by_email = {c.email.lower(): c for c in db.query(Customer).all()}
        products = {p.product_code: p for p in db.query(Product).all()}
        orders = {o.order_number: o for o in db.query(Order).all()}

        orders_count = 0
        items_count = 0
        customers_count = 0
        products_count = 0

        # Pass 1: Upsert Categories, Locations, Customers, Products
        for _, row in df.iterrows():
            row_dict = row.to_dict()

            # Ensure Category
            category_name = row_dict.get("category", "General") or "General"
            cat_key = str(category_name).lower().strip()
            if cat_key not in categories:
                new_cat = Category(
                    name=str(category_name).title().strip(),
                    slug=cat_key.replace(" ", "-").replace("&", "and"),
                    description=f"Auto-generated category {category_name}",
                )
                db.add(new_cat)
                db.flush()
                categories[cat_key] = new_cat

            # Ensure Location if city/state/country present
            city = str(row_dict.get("city", "")).strip()
            state = str(row_dict.get("state", "")).strip() or None
            country = str(row_dict.get("country", "USA")).strip() or "USA"
            loc_obj = None
            if city:
                loc_key = f"{city.lower()}:{state.lower() if state else ''}:{country.lower()}"
                if loc_key not in locations:
                    new_loc = Location(
                        city=city.title(),
                        state=state.title() if state else None,
                        country=country.upper() if len(country) <= 3 else country.title(),
                    )
                    db.add(new_loc)
                    db.flush()
                    locations[loc_key] = new_loc
                loc_obj = locations[loc_key]

            # Ensure Customer
            cust_email = str(row_dict.get("customer_email") or row_dict.get("email") or "").lower().strip()
            if cust_email:
                hash_suffix = hashlib.md5(cust_email.encode("utf-8")).hexdigest()[:8].upper()
                default_code = f"CUST-{hash_suffix}"
            else:
                default_code = f"CUST-{uuid.uuid4().hex[:8].upper()}"
            cust_code = str(row_dict.get("customer_code") or default_code).strip()

            if cust_email and cust_email not in customers_by_email:
                first_name = str(row_dict.get("first_name", "Valued")).strip() or "Valued"
                last_name = str(row_dict.get("last_name", "Customer")).strip() or "Customer"
                phone = str(row_dict.get("phone", "")).strip() or None
                tier = str(row_dict.get("tier", "Bronze")).strip()

                new_cust = Customer(
                    customer_code=cust_code or f"CUST-{len(customers) + 1:04d}",
                    first_name=first_name,
                    last_name=last_name,
                    email=cust_email,
                    phone=phone,
                    location_id=loc_obj.id if loc_obj else None,
                    tier=tier,
                )
                db.add(new_cust)
                db.flush()
                customers[new_cust.customer_code] = new_cust
                customers_by_email[cust_email] = new_cust
                customers_count += 1
            elif cust_email and loc_obj and customers_by_email[cust_email].location_id is None:
                customers_by_email[cust_email].location_id = loc_obj.id

            # Ensure Product
            prod_code = str(row_dict.get("product_code", "")).strip()
            if prod_code and prod_code not in products:
                prod_name = str(row_dict.get("product_name") or row_dict.get("name") or f"Product {prod_code}").strip()
                unit_price = float(row_dict.get("unit_price", 0.0))
                cost_price = float(row_dict.get("cost_price", unit_price * 0.6))
                currency = str(row_dict.get("currency", "USD"))

                new_prod = Product(
                    product_code=prod_code,
                    name=prod_name,
                    category_id=categories[cat_key].id,
                    unit_price=unit_price,
                    cost_price=cost_price,
                    currency=currency,
                    stock_quantity=int(row_dict.get("stock_quantity", 100)),
                )
                db.add(new_prod)
                db.flush()
                products[prod_code] = new_prod
                products_count += 1

        # Pass 2: Upsert Orders and Order Items
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            order_num = str(row_dict.get("order_number", "")).strip()
            if not order_num:
                continue

            cust_email = str(row_dict.get("customer_email") or row_dict.get("email") or "").lower().strip()
            cust_obj = customers_by_email.get(cust_email)
            if not cust_obj:
                continue

            order_date = row_dict.get("order_date")
            if not isinstance(order_date, datetime):
                order_date = datetime.now(timezone.utc)

            total_amount = float(row_dict.get("total_amount") or row_dict.get("item_total_usd") or 0.0)
            currency = str(row_dict.get("currency", "USD"))

            if order_num not in orders:
                order_obj = Order(
                    order_number=order_num,
                    customer_id=cust_obj.id,
                    order_date=order_date,
                    status=str(row_dict.get("status", "Completed")).title(),
                    total_amount=total_amount,
                    currency=currency,
                    shipping_amount=float(row_dict.get("shipping_amount", 5.0)),
                )
                db.add(order_obj)
                db.flush()
                orders[order_num] = order_obj
                orders_count += 1
            else:
                order_obj = orders[order_num]
                # Increment total amount if multiple lines
                order_obj.total_amount += total_amount

            # Add Order Item if product is present
            prod_code = str(row_dict.get("product_code", "")).strip()
            if prod_code and prod_code in products:
                prod_obj = products[prod_code]
                qty = int(row_dict.get("quantity", 1))
                unit_price = float(row_dict.get("unit_price", prod_obj.unit_price))
                discount = float(row_dict.get("discount", 0.0))
                tax = float(row_dict.get("tax", 0.0))
                item_total = float(row_dict.get("item_total", (qty * unit_price) - discount + tax))

                item = OrderItem(
                    order_id=order_obj.id,
                    product_id=prod_obj.id,
                    quantity=qty,
                    unit_price=unit_price,
                    discount=discount,
                    tax=tax,
                    item_total=item_total,
                )
                db.add(item)
                items_count += 1

        summary["inserted_records"] = orders_count + items_count + customers_count + products_count
        summary["entities_affected"] = {
            "orders": orders_count,
            "order_items": items_count,
            "customers": customers_count,
            "products": products_count,
        }
        logger.info("Retail batch loaded", entities=summary["entities_affected"])

    def _load_banking(self, df: pd.DataFrame, db: Session, summary: Dict[str, Any]) -> None:
        """Load banking data (accounts, merchants, transactions)."""
        accounts = {a.account_number: a for a in db.query(BankAccount).all()}
        merchants = {m.merchant_name.lower(): m for m in db.query(Merchant).all()}
        txns = {t.transaction_ref: t for t in db.query(Transaction).all()}

        accounts_count = 0
        merchants_count = 0
        txns_count = 0

        for _, row in df.iterrows():
            row_dict = row.to_dict()

            # Ensure Bank Account
            acc_num = str(row_dict.get("account_number", "")).strip()
            if acc_num and acc_num not in accounts:
                acc_type = str(row_dict.get("account_type", "Checking")).title()
                cust_name = str(row_dict.get("customer_name") or row_dict.get("account_holder") or "Primary Customer").strip()
                curr = str(row_dict.get("currency", "USD"))
                init_balance = float(row_dict.get("balance", 10000.0))

                acc = BankAccount(
                    account_number=acc_num,
                    account_type=acc_type,
                    customer_name=cust_name,
                    currency=curr,
                    balance=init_balance,
                    status="Active",
                )
                db.add(acc)
                db.flush()
                accounts[acc_num] = acc
                accounts_count += 1

            # Ensure Merchant
            merchant_name = str(row_dict.get("merchant_name", "")).strip()
            merchant_obj = None
            if merchant_name:
                m_key = merchant_name.lower()
                if m_key not in merchants:
                    m_obj = Merchant(
                        merchant_name=merchant_name,
                        category=str(row_dict.get("category", "General")),
                    )
                    db.add(m_obj)
                    db.flush()
                    merchants[m_key] = m_obj
                    merchants_count += 1
                merchant_obj = merchants[m_key]

            # Insert Transaction
            txn_ref = str(row_dict.get("transaction_ref", "")).strip()
            if txn_ref and txn_ref not in txns and acc_num in accounts:
                acc_obj = accounts[acc_num]
                txn_date = row_dict.get("transaction_date")
                if not isinstance(txn_date, datetime):
                    txn_date = datetime.now(timezone.utc)

                amount = float(row_dict.get("amount", 0.0))
                amount_usd = float(row_dict.get("amount_usd", amount))
                is_expense = bool(row_dict.get("is_expense", True))
                is_emi = bool(row_dict.get("is_emi", False))

                # Update Account Balance
                if is_expense:
                    acc_obj.balance -= amount
                else:
                    acc_obj.balance += amount

                txn = Transaction(
                    transaction_ref=txn_ref,
                    account_id=acc_obj.id,
                    merchant_id=merchant_obj.id if merchant_obj else None,
                    transaction_date=txn_date,
                    amount=amount,
                    currency=str(row_dict.get("currency", "USD")),
                    amount_usd=amount_usd,
                    transaction_type=str(row_dict.get("transaction_type", "Debit")),
                    category=str(row_dict.get("category", "General")),
                    description=str(row_dict.get("description", "")),
                    is_expense=is_expense,
                    is_emi=is_emi,
                    balance_after=acc_obj.balance,
                )
                db.add(txn)
                txns[txn_ref] = txn
                txns_count += 1

        summary["inserted_records"] = txns_count + accounts_count + merchants_count
        summary["entities_affected"] = {
            "transactions": txns_count,
            "bank_accounts": accounts_count,
            "merchants": merchants_count,
        }
        logger.info("Banking batch loaded", entities=summary["entities_affected"])
