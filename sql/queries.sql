-- =============================================================================
--  Bluestock Fintech — Mutual Fund Capstone Project
--  Day 2: Analytical SQL Queries
--
--  File: queries.sql
--  Database: bluestock_mf.db (SQLite)
--  Contains: 10 analytical queries for mutual fund analysis
-- =============================================================================


-- =============================================================================
-- QUERY 1: Top 5 Funds by AUM (Assets Under Management)
-- Business: Identify the largest funds to understand market concentration.
-- =============================================================================
SELECT
    fp.amfi_code,
    fp.scheme_name,
    fp.fund_house,
    fp.category,
    fp.aum_crore,
    fp.expense_ratio_pct,
    fp.morningstar_rating
FROM fact_performance fp
ORDER BY fp.aum_crore DESC
LIMIT 5;


-- =============================================================================
-- QUERY 2: Average NAV Per Month (across all Large Cap funds)
-- Business: Track monthly NAV trend to observe market performance.
-- =============================================================================
SELECT
    dd.year,
    dd.month,
    dd.month_name,
    ROUND(AVG(fn.nav), 4) AS avg_nav,
    COUNT(DISTINCT fn.amfi_code) AS num_schemes,
    ROUND(MIN(fn.nav), 4) AS min_nav,
    ROUND(MAX(fn.nav), 4) AS max_nav
FROM fact_nav fn
JOIN dim_date dd ON fn.date = dd.date_key
JOIN dim_fund df ON fn.amfi_code = df.amfi_code
WHERE df.sub_category = 'Large Cap'
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;


-- =============================================================================
-- QUERY 3: SIP Year-Over-Year Growth
-- Business: Measure SIP momentum — a key indicator of retail investor confidence.
-- =============================================================================
SELECT
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    sip_aum_lakh_crore,
    ROUND(yoy_growth_pct, 2) AS yoy_growth_pct
FROM fact_sip_inflows
WHERE yoy_growth_pct IS NOT NULL
ORDER BY month;


-- =============================================================================
-- QUERY 4: Transaction Count and Volume by State (Top 10)
-- Business: Identify geographic concentration of MF investors.
-- =============================================================================
SELECT
    ft.state,
    COUNT(*) AS total_transactions,
    SUM(ft.amount_inr) AS total_volume_inr,
    ROUND(AVG(ft.amount_inr), 0) AS avg_transaction_size,
    COUNT(DISTINCT ft.investor_id) AS unique_investors,
    ROUND(SUM(ft.amount_inr) * 1.0 / COUNT(DISTINCT ft.investor_id), 0) AS avg_volume_per_investor
FROM fact_transactions ft
GROUP BY ft.state
ORDER BY total_volume_inr DESC
LIMIT 10;


-- =============================================================================
-- QUERY 5: Funds with Expense Ratio Below 1%
-- Business: Identify cost-efficient funds — important for long-term investors.
-- =============================================================================
SELECT
    df.amfi_code,
    df.scheme_name,
    df.fund_house,
    df.sub_category,
    df.plan,
    df.expense_ratio_pct,
    fp.return_3yr_pct,
    fp.sharpe_ratio,
    fp.morningstar_rating
FROM dim_fund df
JOIN fact_performance fp ON df.amfi_code = fp.amfi_code
WHERE df.expense_ratio_pct < 1.0
ORDER BY df.expense_ratio_pct ASC;


-- =============================================================================
-- QUERY 6: Category-wise Total Net Inflows (Latest 6 Months)
-- Business: Understand which fund categories are attracting/losing money.
-- =============================================================================
SELECT
    category,
    COUNT(*) AS months_covered,
    ROUND(SUM(net_inflow_crore), 0) AS total_net_inflow_crore,
    ROUND(AVG(net_inflow_crore), 0) AS avg_monthly_inflow_crore,
    ROUND(MIN(net_inflow_crore), 0) AS min_monthly_inflow,
    ROUND(MAX(net_inflow_crore), 0) AS max_monthly_inflow
FROM fact_category_inflows
WHERE month >= (SELECT MAX(month) FROM fact_category_inflows LIMIT 1)
   OR month IN (
       SELECT DISTINCT month FROM fact_category_inflows
       ORDER BY month DESC LIMIT 6
   )
GROUP BY category
ORDER BY total_net_inflow_crore DESC;


-- =============================================================================
-- QUERY 7: Fund Performance Alpha Ranking (Top 10 — Beat Benchmark Most)
-- Business: Identify fund managers who consistently generate excess returns.
-- =============================================================================
SELECT
    fp.amfi_code,
    fp.scheme_name,
    fp.fund_house,
    fp.category,
    fp.plan,
    fp.return_3yr_pct,
    fp.benchmark_3yr_pct,
    ROUND(fp.return_3yr_pct - fp.benchmark_3yr_pct, 2) AS outperformance_pct,
    fp.alpha,
    fp.sharpe_ratio,
    fp.morningstar_rating
FROM fact_performance fp
WHERE fp.return_3yr_pct IS NOT NULL
  AND fp.benchmark_3yr_pct IS NOT NULL
ORDER BY outperformance_pct DESC
LIMIT 10;


-- =============================================================================
-- QUERY 8: Monthly Transaction Volume Trend
-- Business: Track investment activity over time for demand forecasting.
-- =============================================================================
SELECT
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(*) AS num_transactions,
    SUM(CASE WHEN ft.transaction_type = 'SIP' THEN 1 ELSE 0 END) AS sip_count,
    SUM(CASE WHEN ft.transaction_type = 'Lumpsum' THEN 1 ELSE 0 END) AS lumpsum_count,
    SUM(CASE WHEN ft.transaction_type = 'Redemption' THEN 1 ELSE 0 END) AS redemption_count,
    SUM(ft.amount_inr) AS total_amount_inr,
    ROUND(AVG(ft.amount_inr), 0) AS avg_amount_inr
FROM fact_transactions ft
JOIN dim_date dd ON ft.transaction_date = dd.date_key
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;


-- =============================================================================
-- QUERY 9: Investor Demographics — Gender Split by Transaction Type
-- Business: Understand investor profiles for targeted product development.
-- =============================================================================
SELECT
    ft.gender,
    ft.transaction_type,
    COUNT(*) AS num_transactions,
    SUM(ft.amount_inr) AS total_amount_inr,
    ROUND(AVG(ft.amount_inr), 0) AS avg_amount_inr,
    ROUND(AVG(ft.annual_income_lakh), 1) AS avg_income_lakh,
    COUNT(DISTINCT ft.investor_id) AS unique_investors
FROM fact_transactions ft
GROUP BY ft.gender, ft.transaction_type
ORDER BY ft.gender, ft.transaction_type;


-- =============================================================================
-- QUERY 10: Risk-Grade-Wise Average Sharpe Ratio & Returns
-- Business: Compare risk-adjusted returns across risk categories to help
--           investors choose appropriate funds based on risk appetite.
-- =============================================================================
SELECT
    fp.risk_grade,
    COUNT(*) AS num_funds,
    ROUND(AVG(fp.sharpe_ratio), 3) AS avg_sharpe_ratio,
    ROUND(AVG(fp.sortino_ratio), 3) AS avg_sortino_ratio,
    ROUND(AVG(fp.return_1yr_pct), 2) AS avg_return_1yr,
    ROUND(AVG(fp.return_3yr_pct), 2) AS avg_return_3yr,
    ROUND(AVG(fp.return_5yr_pct), 2) AS avg_return_5yr,
    ROUND(AVG(fp.std_dev_ann_pct), 2) AS avg_std_dev,
    ROUND(AVG(fp.max_drawdown_pct), 2) AS avg_max_drawdown,
    ROUND(AVG(fp.expense_ratio_pct), 2) AS avg_expense_ratio
FROM fact_performance fp
GROUP BY fp.risk_grade
ORDER BY avg_sharpe_ratio DESC;
