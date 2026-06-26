-- =============================================================================
--  Bluestock Fintech — Mutual Fund Capstone Project
--  Day 2: SQLite Star Schema
--
--  File: schema.sql
--  Purpose: CREATE TABLE statements for star-schema database
--           with dimension and fact tables.
-- =============================================================================

-- =============================================
-- DIMENSION TABLES
-- =============================================

-- dim_fund: Fund/scheme metadata (from fund_master)
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    fund_house          TEXT NOT NULL,
    scheme_name         TEXT NOT NULL,
    category            TEXT NOT NULL,
    sub_category        TEXT NOT NULL,
    plan                TEXT NOT NULL,          -- 'Regular' or 'Direct'
    launch_date         TEXT,                   -- YYYY-MM-DD
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

-- dim_date: Date dimension (generated for all dates in the dataset range)
CREATE TABLE IF NOT EXISTS dim_date (
    date_key        TEXT PRIMARY KEY,       -- YYYY-MM-DD
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,       -- 1-4
    month           INTEGER NOT NULL,       -- 1-12
    month_name      TEXT NOT NULL,          -- 'January', etc.
    day             INTEGER NOT NULL,
    day_of_week     INTEGER NOT NULL,       -- 0=Monday, 6=Sunday
    day_name        TEXT NOT NULL,          -- 'Monday', etc.
    week_of_year    INTEGER NOT NULL,
    is_weekend      INTEGER NOT NULL,       -- 0 or 1
    is_month_end    INTEGER NOT NULL,       -- 0 or 1
    is_quarter_end  INTEGER NOT NULL,       -- 0 or 1
    fiscal_year     INTEGER NOT NULL        -- Indian FY (Apr-Mar)
);


-- =============================================
-- FACT TABLES
-- =============================================

-- fact_nav: Daily NAV values per scheme
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code       INTEGER NOT NULL,
    date            TEXT NOT NULL,
    nav             REAL NOT NULL CHECK(nav > 0),
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date_key)
);

-- fact_transactions: Individual investor transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT NOT NULL,
    transaction_date    TEXT NOT NULL,
    amfi_code           INTEGER NOT NULL,
    transaction_type    TEXT NOT NULL CHECK(transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount_inr          INTEGER NOT NULL CHECK(amount_inr > 0),
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT CHECK(kyc_status IN ('Verified', 'Pending')),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date_key)
);

-- fact_performance: Scheme performance metrics
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code           INTEGER PRIMARY KEY,
    scheme_name         TEXT NOT NULL,
    fund_house          TEXT NOT NULL,
    category            TEXT,
    plan                TEXT,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           INTEGER,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER CHECK(morningstar_rating BETWEEN 1 AND 5),
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- fact_aum: AUM by fund house over time
CREATE TABLE IF NOT EXISTS fact_aum (
    date            TEXT NOT NULL,
    fund_house      TEXT NOT NULL,
    aum_lakh_crore  REAL,
    aum_crore       INTEGER,
    num_schemes     INTEGER,
    PRIMARY KEY (date, fund_house),
    FOREIGN KEY (date) REFERENCES dim_date(date_key)
);

-- fact_sip_inflows: Monthly SIP inflow data
CREATE TABLE IF NOT EXISTS fact_sip_inflows (
    month                       TEXT PRIMARY KEY,
    sip_inflow_crore            INTEGER,
    active_sip_accounts_crore   REAL,
    new_sip_accounts_lakh       REAL,
    sip_aum_lakh_crore          REAL,
    yoy_growth_pct              REAL
);

-- fact_category_inflows: Category-wise monthly net inflows
CREATE TABLE IF NOT EXISTS fact_category_inflows (
    month           TEXT NOT NULL,
    category        TEXT NOT NULL,
    net_inflow_crore REAL,
    PRIMARY KEY (month, category)
);


-- =============================================
-- ADDITIONAL TABLES (Not strict star-schema but needed for analysis)
-- =============================================

-- industry_folio_count: Quarterly folio counts
CREATE TABLE IF NOT EXISTS industry_folio_count (
    month                   TEXT PRIMARY KEY,
    total_folios_crore      REAL,
    equity_folios_crore     REAL,
    debt_folios_crore       REAL,
    hybrid_folios_crore     REAL,
    others_folios_crore     REAL
);

-- portfolio_holdings: Stock-level holdings per scheme
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    amfi_code           INTEGER NOT NULL,
    stock_symbol        TEXT NOT NULL,
    stock_name          TEXT,
    sector              TEXT,
    weight_pct          REAL,
    market_value_cr     REAL,
    current_price_inr   REAL,
    portfolio_date      TEXT,
    PRIMARY KEY (amfi_code, stock_symbol, portfolio_date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- benchmark_indices: Daily benchmark index values
CREATE TABLE IF NOT EXISTS benchmark_indices (
    date            TEXT NOT NULL,
    index_name      TEXT NOT NULL,
    close_value     REAL NOT NULL,
    PRIMARY KEY (date, index_name),
    FOREIGN KEY (date) REFERENCES dim_date(date_key)
);


-- =============================================
-- INDEXES for query performance
-- =============================================
CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date);
CREATE INDEX IF NOT EXISTS idx_fact_nav_code ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_txn_date ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_fact_txn_code ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_txn_type ON fact_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_fact_txn_state ON fact_transactions(state);
CREATE INDEX IF NOT EXISTS idx_benchmark_date ON benchmark_indices(date);
CREATE INDEX IF NOT EXISTS idx_benchmark_name ON benchmark_indices(index_name);
CREATE INDEX IF NOT EXISTS idx_holdings_code ON portfolio_holdings(amfi_code);
