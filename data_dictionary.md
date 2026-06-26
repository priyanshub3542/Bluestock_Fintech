# 📖 Bluestock MF — Data Dictionary

> **Project:** Mutual Fund Analytics Capstone  
> **Version:** Day 2  
> **Last Updated:** 2026-06-26  
> **Database:** `bluestock_mf.db` (SQLite)

---

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Dimension Tables](#dimension-tables)
   - [dim_fund](#dim_fund)
   - [dim_date](#dim_date)
3. [Fact Tables](#fact-tables)
   - [fact_nav](#fact_nav)
   - [fact_transactions](#fact_transactions)
   - [fact_performance](#fact_performance)
   - [fact_aum](#fact_aum)
   - [fact_sip_inflows](#fact_sip_inflows)
   - [fact_category_inflows](#fact_category_inflows)
4. [Additional Tables](#additional-tables)
   - [industry_folio_count](#industry_folio_count)
   - [portfolio_holdings](#portfolio_holdings)
   - [benchmark_indices](#benchmark_indices)
5. [Relationships](#relationships)
6. [Data Lineage](#data-lineage)
7. [Enumerations & Valid Values](#enumerations--valid-values)

---

## Schema Overview

The database follows a **star schema** design with 2 dimension tables and 6 fact tables, plus 3 additional supporting tables.

```
                    ┌──────────┐
                    │ dim_date │
                    └────┬─────┘
                         │
    ┌──────────┐    ┌────┴──────┐    ┌─────────────────┐
    │ dim_fund ├────┤ fact_nav  │    │ fact_sip_inflows │
    └────┬─────┘    └───────────┘    └─────────────────┘
         │
         ├──── fact_transactions     fact_category_inflows
         │
         ├──── fact_performance      industry_folio_count
         │
         ├──── portfolio_holdings    benchmark_indices
         │
         └──── fact_aum
```

---

## Dimension Tables

### dim_fund

**Description:** Master reference table containing metadata for all 40 mutual fund schemes tracked in this project.  
**Source:** `01_fund_master.csv`  
**Grain:** One row per unique AMFI scheme code  
**Record Count:** 40

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `amfi_code` | INTEGER | **PK** | No | AMFI (Association of Mutual Funds in India) unique scheme identifier | 100016 – 149324 |
| `fund_house` | TEXT | — | No | Name of the Asset Management Company (AMC) | "SBI Mutual Fund", "HDFC Mutual Fund" |
| `scheme_name` | TEXT | — | No | Full official scheme name including plan type | "SBI Bluechip Fund - Regular Plan - Growth" |
| `category` | TEXT | — | No | Broad asset class category | "Equity", "Debt" |
| `sub_category` | TEXT | — | No | SEBI sub-classification of the fund | "Large Cap", "Mid Cap", "Small Cap", "Liquid", "Gilt" |
| `plan` | TEXT | — | No | Distribution plan type | "Regular", "Direct" |
| `launch_date` | TEXT | — | Yes | Fund launch/inception date (YYYY-MM-DD) | "2006-02-14" |
| `benchmark` | TEXT | — | Yes | Benchmark index used for performance comparison | "NIFTY 100 TRI" |
| `expense_ratio_pct` | REAL | — | Yes | Total expense ratio charged to investors (%) | 0.55 – 1.64 |
| `exit_load_pct` | REAL | — | Yes | Exit load penalty for early redemption (%) | 0.0 or 1.0 |
| `min_sip_amount` | INTEGER | — | Yes | Minimum SIP investment amount (INR) | 500 |
| `min_lumpsum_amount` | INTEGER | — | Yes | Minimum lumpsum investment amount (INR) | 100 – 5000 |
| `fund_manager` | TEXT | — | Yes | Name of the fund manager | "Sohini Andani" |
| `risk_category` | TEXT | — | Yes | Risk classification of the fund | "Low", "Moderate", "Moderately High", "High", "Very High" |
| `sebi_category_code` | TEXT | — | Yes | SEBI standardized category code | "EC01", "DC01", "EI01" |

---

### dim_date

**Description:** Calendar dimension table providing date attributes for time-based analysis. Covers 2000-01-01 to 2027-12-31.  
**Source:** Generated programmatically  
**Grain:** One row per calendar day  
**Record Count:** ~10,227

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `date_key` | TEXT | **PK** | No | Date in ISO format (YYYY-MM-DD) | "2024-01-15" |
| `year` | INTEGER | — | No | Calendar year | 2000 – 2027 |
| `quarter` | INTEGER | — | No | Calendar quarter | 1 – 4 |
| `month` | INTEGER | — | No | Calendar month number | 1 – 12 |
| `month_name` | TEXT | — | No | Full month name | "January" – "December" |
| `day` | INTEGER | — | No | Day of month | 1 – 31 |
| `day_of_week` | INTEGER | — | No | Day of week (ISO: 0=Monday, 6=Sunday) | 0 – 6 |
| `day_name` | TEXT | — | No | Full day name | "Monday" – "Sunday" |
| `week_of_year` | INTEGER | — | No | ISO week number | 1 – 53 |
| `is_weekend` | INTEGER | — | No | Weekend flag | 0 (weekday), 1 (weekend) |
| `is_month_end` | INTEGER | — | No | Last day of month flag | 0 or 1 |
| `is_quarter_end` | INTEGER | — | No | Last day of quarter flag | 0 or 1 |
| `fiscal_year` | INTEGER | — | No | Indian fiscal year (Apr–Mar). FY2025 = Apr 2024 – Mar 2025 | 2000 – 2028 |

---

## Fact Tables

### fact_nav

**Description:** Daily Net Asset Value (NAV) for each mutual fund scheme. NAV represents the per-unit market value of the fund. Business-day gaps (weekends/holidays) are forward-filled.  
**Source:** `02_nav_history.csv`  
**Grain:** One row per (scheme, business day)  
**Record Count:** ~46,000+ (with forward-fill)

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `amfi_code` | INTEGER | **PK**, FK→dim_fund | No | AMFI scheme code | 100016 – 149324 |
| `date` | TEXT | **PK**, FK→dim_date | No | NAV date (YYYY-MM-DD) | "2022-01-03" – "2026-05-29" |
| `nav` | REAL | — | No | Net Asset Value per unit (INR) | Must be > 0 |

---

### fact_transactions

**Description:** Individual mutual fund transactions by retail investors including SIPs, lumpsum investments, and redemptions. Contains demographic and geographic data.  
**Source:** `08_investor_transactions.csv`  
**Grain:** One row per individual transaction  
**Record Count:** ~32,778

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `txn_id` | INTEGER | **PK** (auto) | No | Auto-generated transaction ID | Auto-increment |
| `investor_id` | TEXT | — | No | Unique investor identifier | "INV000001" – "INV005000" |
| `transaction_date` | TEXT | FK→dim_date | No | Transaction date (YYYY-MM-DD) | "2024-01-01" – "2025-05-30" |
| `amfi_code` | INTEGER | FK→dim_fund | No | Scheme AMFI code invested in | 100016 – 149324 |
| `transaction_type` | TEXT | — | No | Type of transaction | "SIP", "Lumpsum", "Redemption" |
| `amount_inr` | INTEGER | — | No | Transaction amount in INR | Must be > 0 |
| `state` | TEXT | — | Yes | Indian state of investor | "Maharashtra", "Delhi", etc. |
| `city` | TEXT | — | Yes | City of investor | "Mumbai", "Bangalore", etc. |
| `city_tier` | TEXT | — | Yes | AMFI city classification | "T30" (Top 30), "B30" (Beyond 30) |
| `age_group` | TEXT | — | Yes | Age bracket of investor | "18-25", "26-35", "36-45", "46-55", "56+" |
| `gender` | TEXT | — | Yes | Gender of investor | "Male", "Female" |
| `annual_income_lakh` | REAL | — | Yes | Annual income in lakhs INR | Positive values |
| `payment_mode` | TEXT | — | Yes | Payment method used | "UPI", "Net Banking", "Mandate", "Cheque" |
| `kyc_status` | TEXT | — | Yes | KYC verification status | "Verified", "Pending" |

---

### fact_performance

**Description:** Performance metrics, risk ratios, and ratings for each scheme. Includes return percentages, risk-adjusted metrics (Sharpe, Sortino, Alpha, Beta), and external ratings.  
**Source:** `07_scheme_performance.csv`  
**Grain:** One row per scheme  
**Record Count:** 40

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `amfi_code` | INTEGER | **PK**, FK→dim_fund | No | AMFI scheme code | 100016 – 149324 |
| `scheme_name` | TEXT | — | No | Scheme name | Descriptive text |
| `fund_house` | TEXT | — | No | AMC name | "SBI Mutual Fund", etc. |
| `category` | TEXT | — | Yes | Fund sub-category | "Large Cap", "Mid Cap", etc. |
| `plan` | TEXT | — | Yes | Regular or Direct | "Regular", "Direct" |
| `return_1yr_pct` | REAL | — | Yes | 1-year trailing return (%) | Can be negative |
| `return_3yr_pct` | REAL | — | Yes | 3-year CAGR return (%) | Can be negative |
| `return_5yr_pct` | REAL | — | Yes | 5-year CAGR return (%) | Can be negative |
| `benchmark_3yr_pct` | REAL | — | Yes | Benchmark 3-year CAGR (%) | Reference value |
| `alpha` | REAL | — | Yes | Jensen's Alpha — excess return over benchmark (risk-adjusted) | Positive = outperformance |
| `beta` | REAL | — | Yes | Systematic risk relative to market. 1.0 = moves with market | Typically 0.2 – 1.5 |
| `sharpe_ratio` | REAL | — | Yes | Risk-adjusted return: (Return - Risk-free rate) / Std Dev | Higher = better |
| `sortino_ratio` | REAL | — | Yes | Like Sharpe but only penalizes downside volatility | Higher = better |
| `std_dev_ann_pct` | REAL | — | Yes | Annualized standard deviation of returns (%) — volatility measure | 0.5 – 25.0 |
| `max_drawdown_pct` | REAL | — | Yes | Maximum peak-to-trough decline (%) — worst-case loss | Negative values |
| `aum_crore` | INTEGER | — | Yes | Assets Under Management in crores INR | Positive values |
| `expense_ratio_pct` | REAL | — | Yes | Total expense ratio (%) | Typically 0.1 – 2.5 |
| `morningstar_rating` | INTEGER | — | Yes | Morningstar star rating | 1 – 5 (5 = best) |
| `risk_grade` | TEXT | — | Yes | Qualitative risk assessment | "Low", "Moderate", "Moderately High", "High", "Very High" |

---

### fact_aum

**Description:** Quarterly Assets Under Management (AUM) data by fund house, tracking the size and growth of each AMC.  
**Source:** `03_aum_by_fund_house.csv`  
**Grain:** One row per (fund house, quarter-end date)  
**Record Count:** 90

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `date` | TEXT | **PK**, FK→dim_date | No | Quarter-end date (YYYY-MM-DD) | "2022-03-31" – "2025-03-31" |
| `fund_house` | TEXT | **PK** | No | AMC name | "SBI Mutual Fund", etc. |
| `aum_lakh_crore` | REAL | — | Yes | AUM in lakh crores INR | 1.0 – 8.0 |
| `aum_crore` | INTEGER | — | Yes | AUM in crores INR | 100,000 – 800,000 |
| `num_schemes` | INTEGER | — | Yes | Total active schemes of the fund house | 50 – 220 |

---

### fact_sip_inflows

**Description:** Monthly industry-level SIP (Systematic Investment Plan) data capturing inflow amounts, account counts, and AUM.  
**Source:** `04_monthly_sip_inflows.csv`  
**Grain:** One row per month  
**Record Count:** 48

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `month` | TEXT | **PK** | No | Month (YYYY-MM-DD, first of month) | "2022-01-01" – "2025-12-01" |
| `sip_inflow_crore` | INTEGER | — | Yes | Total SIP inflow in crores INR for the month | 10,000 – 30,000 |
| `active_sip_accounts_crore` | REAL | — | Yes | Number of active SIP accounts (in crores) | 4.0 – 10.0 |
| `new_sip_accounts_lakh` | REAL | — | Yes | New SIP registrations in the month (in lakhs) | 5.0 – 15.0 |
| `sip_aum_lakh_crore` | REAL | — | Yes | Total SIP AUM (in lakh crores INR) | 4.0 – 13.0 |
| `yoy_growth_pct` | REAL | — | Yes | Year-over-year SIP inflow growth (%). NULL for first 12 months | Can be negative |

---

### fact_category_inflows

**Description:** Monthly net fund inflows/outflows broken down by mutual fund category. Positive values indicate net inflows, negative values indicate net outflows.  
**Source:** `05_category_inflows.csv`  
**Grain:** One row per (month, category)  
**Record Count:** 144

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `month` | TEXT | **PK** | No | Month (YYYY-MM-DD) | "2024-04-01" – "2025-03-01" |
| `category` | TEXT | **PK** | No | Fund category | "Large Cap", "Liquid", "Sectoral/Thematic", etc. |
| `net_inflow_crore` | REAL | — | Yes | Net inflow/outflow in crores INR | Can be negative (outflow) |

---

## Additional Tables

### industry_folio_count

**Description:** Quarterly snapshot of total mutual fund folios (accounts) across the industry, segmented by asset class.  
**Source:** `06_industry_folio_count.csv`  
**Grain:** One row per quarter  
**Record Count:** 21

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `month` | TEXT | **PK** | No | Quarter start date (YYYY-MM-DD) | "2022-01-01" – "2025-04-01" |
| `total_folios_crore` | REAL | — | Yes | Total industry folios (crores) | 13.0 – 24.0 |
| `equity_folios_crore` | REAL | — | Yes | Equity fund folios (crores) | 9.0 – 17.0 |
| `debt_folios_crore` | REAL | — | Yes | Debt fund folios (crores) | 1.8 – 3.3 |
| `hybrid_folios_crore` | REAL | — | Yes | Hybrid fund folios (crores) | 0.8 – 1.4 |
| `others_folios_crore` | REAL | — | Yes | Other category folios (crores) | 1.3 – 2.4 |

---

### portfolio_holdings

**Description:** Stock-level portfolio composition for each scheme. Shows individual stock weights, market values, and sector allocation.  
**Source:** `09_portfolio_holdings.csv`  
**Grain:** One row per (scheme, stock, date)  
**Record Count:** 322

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `amfi_code` | INTEGER | **PK**, FK→dim_fund | No | AMFI scheme code | 100016 – 149324 |
| `stock_symbol` | TEXT | **PK** | No | NSE/BSE stock ticker symbol | "HDFCBANK", "TCS", "INFY" |
| `stock_name` | TEXT | — | Yes | Full company name | "HDFC Bank Ltd" |
| `sector` | TEXT | — | Yes | Industry sector classification | "Banking", "IT", "Pharma", etc. |
| `weight_pct` | REAL | — | Yes | Portfolio weight of the stock (%) | 0.0 – 100.0 |
| `market_value_cr` | REAL | — | Yes | Market value of holding in crores INR | Positive values |
| `current_price_inr` | REAL | — | Yes | Current market price per share (INR) | Positive values |
| `portfolio_date` | TEXT | **PK** | Yes | Portfolio disclosure date (YYYY-MM-DD) | "2025-12-31" |

---

### benchmark_indices

**Description:** Daily closing values for major Indian market benchmark indices used for fund performance comparison.  
**Source:** `10_benchmark_indices.csv`  
**Grain:** One row per (index, date)  
**Record Count:** 8,050

| Column | Data Type | PK/FK | Nullable | Description | Valid Range / Example |
|--------|-----------|-------|----------|-------------|---------------------|
| `date` | TEXT | **PK**, FK→dim_date | No | Trading date (YYYY-MM-DD) | "2022-01-03" – "2026-05-29" |
| `index_name` | TEXT | **PK** | No | Benchmark index identifier | See index list below |
| `close_value` | REAL | — | No | Daily closing value of the index | Must be > 0 |

**Index Names:**
- `NIFTY50` — NIFTY 50 (Top 50 large-cap stocks)
- `NIFTY100` — NIFTY 100 (Top 100 stocks)
- `NIFTY_MIDCAP150` — NIFTY Midcap 150
- `BSE_SMALLCAP` — BSE 250 SmallCap
- `NIFTY500` — NIFTY 500 (Broad market)
- `CRISIL_LIQUID` — CRISIL Liquid Fund AI Index
- `CRISIL_GILT` — CRISIL Dynamic Gilt Index

---

## Relationships

```
dim_fund.amfi_code ──┬──> fact_nav.amfi_code
                     ├──> fact_transactions.amfi_code
                     ├──> fact_performance.amfi_code
                     └──> portfolio_holdings.amfi_code

dim_date.date_key  ──┬──> fact_nav.date
                     ├──> fact_transactions.transaction_date
                     ├──> fact_aum.date
                     └──> benchmark_indices.date
```

---

## Data Lineage

```
Raw CSVs (data/raw/)          Cleaned CSVs (data/processed/)     SQLite Tables
─────────────────────         ──────────────────────────────     ─────────────
01_fund_master.csv       ──>  01_fund_master.csv            ──>  dim_fund
                              (generated)                   ──>  dim_date
02_nav_history.csv       ──>  02_nav_history.csv            ──>  fact_nav
03_aum_by_fund_house.csv ──>  03_aum_by_fund_house.csv      ──>  fact_aum
04_monthly_sip_inflows.csv -> 04_monthly_sip_inflows.csv    ──>  fact_sip_inflows
05_category_inflows.csv  ──>  05_category_inflows.csv       ──>  fact_category_inflows
06_industry_folio_count.csv > 06_industry_folio_count.csv   ──>  industry_folio_count
07_scheme_performance.csv ->  07_scheme_performance.csv      ──>  fact_performance
08_investor_transactions.csv> 08_investor_transactions.csv  ──>  fact_transactions
09_portfolio_holdings.csv ->  09_portfolio_holdings.csv      ──>  portfolio_holdings
10_benchmark_indices.csv ──>  10_benchmark_indices.csv       ──>  benchmark_indices
```

**Cleaning transformations applied:**
- Dates parsed to `YYYY-MM-DD` format across all datasets
- `nav_history`: sorted by scheme+date, forward-filled for business-day gaps, validated NAV > 0
- `investor_transactions`: standardized transaction types, validated amounts, verified KYC enum
- `scheme_performance`: validated numeric columns, flagged expense ratio anomalies
- All datasets: removed duplicates, stripped whitespace from string columns

---

## Enumerations & Valid Values

### Transaction Types
| Value | Description |
|-------|-------------|
| `SIP` | Systematic Investment Plan — recurring monthly investment |
| `Lumpsum` | One-time investment |
| `Redemption` | Withdrawal/selling of fund units |

### Risk Categories
| Value | Typical Funds |
|-------|---------------|
| `Low` | Liquid, Gilt, Short Duration |
| `Moderate` | Large Cap, Index |
| `Moderately High` | Flexi Cap, Value, Large & Mid Cap |
| `High` | Mid Cap, ELSS, Sectoral |
| `Very High` | Small Cap |

### KYC Status
| Value | Description |
|-------|-------------|
| `Verified` | KYC documentation complete and verified |
| `Pending` | KYC verification in progress |

### City Tier (AMFI Classification)
| Value | Description |
|-------|-------------|
| `T30` | Top 30 cities by AUM — metro and major cities |
| `B30` | Beyond 30 — smaller cities and towns |

### Plan Types
| Value | Description |
|-------|-------------|
| `Regular` | Distributed through intermediaries (higher expense ratio) |
| `Direct` | Invested directly with AMC (lower expense ratio) |

### SEBI Category Codes
| Code | Category |
|------|----------|
| `EC01` | Equity — Large Cap |
| `EC02` | Equity — Mid Cap |
| `EC03` | Equity — Small Cap |
| `EC04` | Equity — Flexi Cap / Large & Mid Cap |
| `EC05` | Equity — ELSS |
| `EC06` | Equity — Value/Contra |
| `EI01` | Equity — Index/ETF |
| `DC01` | Debt — Liquid |
| `DC02` | Debt — Gilt / Short Duration |
