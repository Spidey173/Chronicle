# Power BI Dashboard Engineering & Visualization Guide

This guide details connecting Microsoft Power BI to the Chronicle platform, building executive dashboards, and utilizing enterprise DAX formulas.

---

## 1. Connecting Power BI to the Platform

You can connect Power BI using two primary methods:

### Method A: Direct PostgreSQL Connection (Recommended for DirectQuery & Live Reports)

1. Open **Power BI Desktop**.
2. Click **Get Data** → **PostgreSQL database** → **Connect**.
3. Configure the connection dialog:
   * **Server**: `localhost:5432` (or RDS endpoint `chronicle-db.xyz.us-east-1.rds.amazonaws.com`)
   * **Database**: `analytics_db`
   * **Data Connectivity Mode**: **DirectQuery** (for real-time updates) or **Import** (for offline in-memory cache)
4. Enter credentials:
   * **Username**: `postgres` (or `chronicle_admin`)
   * **Password**: `postgres`
5. In the Navigator pane, select the normalized tables:
   * `orders`
   * `order_items`
   * `customers`
   * `products`
   * `categories`
   * `locations`
   * `transactions`
   * `bank_accounts`
   * `merchants`
6. Click **Load**.

### Method B: REST API Web Connector (JSON API Ingestion)

1. Click **Get Data** → **Web**.
2. Select **Advanced**.
3. **URL parts**: `http://localhost:8000/api/v1/analytics/monthly-sales`
4. **HTTP request header parameters**:
   * Header: `Authorization`
   * Value: `Bearer <your_jwt_token>`
5. Click **OK** → Power Query converts JSON to a tabular query.

---

## 2. Recommended Star-Schema Relationships

In Power BI **Model View**, ensure the following single-directional (1-to-many) relationships exist:

| From Table (Fact) | From Column | To Table (Dimension) | To Column | Cardinality |
| :--- | :--- | :--- | :--- | :--- |
| `order_items` | `order_id` | `orders` | `id` | Many-to-1 (`* : 1`) |
| `order_items` | `product_id` | `products` | `id` | Many-to-1 (`* : 1`) |
| `orders` | `customer_id` | `customers` | `id` | Many-to-1 (`* : 1`) |
| `customers` | `location_id` | `locations` | `id` | Many-to-1 (`* : 1`) |
| `products` | `category_id` | `categories` | `id` | Many-to-1 (`* : 1`) |
| `transactions` | `account_id` | `bank_accounts` | `id` | Many-to-1 (`* : 1`) |
| `transactions` | `merchant_id` | `merchants` | `id` | Many-to-1 (`* : 1`) |

---

## 3. Dashboard Reports & Visuals

### Report 1: Executive Retail & E-Commerce Dashboard

1. **KPI Cards (Top Row)**:
   * `[Total Revenue]`: Card visual formatted as currency `$#,##0.00`
   * `[Total Orders]`: Card visual formatted as integer
   * `[Average Order Value]`: Card visual formatted as `$#,##0.00`
   * `[Gross Margin %]`: Card visual formatted as percentage `0.0%`

2. **Monthly Sales & Revenue Trends**:
   * **Visual**: Clustered Column & Line Chart
   * **X-Axis**: `orders[order_date]` (Hierarchy: Year, Month)
   * **Column Y-Axis**: `[Total Revenue]`
   * **Line Y-Axis**: `[MoM Revenue Growth %]`

3. **Product Performance**:
   * **Visual**: Horizontal Bar Chart
   * **Y-Axis**: `products[name]`
   * **X-Axis**: `[Total Revenue]`
   * **Tooltip**: `[Total Units Sold]`, `[Gross Margin %]`

4. **Category Breakdown**:
   * **Visual**: Donut Chart
   * **Legend**: `categories[name]`
   * **Values**: `[Total Revenue]`

5. **Customer Growth & VIP Segments**:
   * **Visual**: Matrix Table
   * **Rows**: `customers[tier]`, `customers[customer_code]`
   * **Values**: `[Total Orders]`, `[Customer Lifetime Spend]`

6. **Regional Performance**:
   * **Visual**: Filled Map or Bubble Map
   * **Location**: `locations[country]`, `locations[city]`
   * **Bubble Size**: `[Total Revenue]`

---

### Report 2: Banking & Financial Transactions Dashboard

1. **Cash Flow KPI Cards**:
   * `[Total Income]`: Card formatted in green
   * `[Total Expenses]`: Card formatted in coral red
   * `[Net Savings]`: Card with conditional formatting
   * `[Savings Rate %]`: Target threshold gauge (> 20%)
   * `[Total EMI Outflow]`: Card highlighting debt servicing

2. **Income vs Expenses Comparison**:
   * **Visual**: Stacked Column Chart or 100% Stacked Bar
   * **X-Axis**: `transactions[transaction_date]` (Month)
   * **Values**: `[Total Income]`, `[Total Expenses]`

3. **Spending by Category**:
   * **Visual**: Treemap
   * **Group**: `transactions[category]`
   * **Values**: `[Total Expenses]`

4. **EMI & Loan Analysis**:
   * **Visual**: Waterfall Chart
   * **Category**: Month / Account
   * **Values**: `[Total EMI Outflow]`
   * **Callout Metric**: `[Debt Service Ratio %]`

5. **Savings Trends**:
   * **Visual**: Area Chart
   * **X-Axis**: Month
   * **Y-Axis**: `[Net Savings]`

---

## 4. DAX Measures Library

Import the pre-written measures located in:
`powerbi/dax_measures.dax`

Or inspect the Tabular Model BIM definitions:
* `powerbi/retail_analytics_model.bim`
* `powerbi/banking_analytics_model.bim`
