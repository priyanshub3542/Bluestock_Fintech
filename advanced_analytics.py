import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

PROC = "data/processed"
CHART_DIR = "reports/charts"
os.makedirs(CHART_DIR, exist_ok=True)

print("Loading datasets...")
nav = pd.read_csv(os.path.join(PROC, '02_nav_history.csv'), parse_dates=['date'])
txn = pd.read_csv(os.path.join(PROC, '08_investor_transactions.csv'), parse_dates=['transaction_date'])
holdings = pd.read_csv(os.path.join(PROC, '09_portfolio_holdings.csv'))
funds = pd.read_csv(os.path.join(PROC, '01_fund_master.csv'))

# ==========================================
# 1. Historical VaR & CVaR (95%)
# ==========================================
print("Computing Historical VaR & CVaR...")
# Calculate daily returns
nav = nav.sort_values(['amfi_code', 'date'])
nav['daily_return'] = nav.groupby('amfi_code')['nav'].pct_change()

var_cvar_results = []
for amfi, group in nav.groupby('amfi_code'):
    returns = group['daily_return'].dropna()
    if len(returns) == 0:
        continue
    # 95% VaR (5th percentile)
    var_95 = np.percentile(returns, 5)
    # CVaR (mean of returns below VaR)
    cvar = returns[returns <= var_95].mean()
    var_cvar_results.append({'amfi_code': amfi, 'var_95_pct': var_95 * 100, 'cvar_pct': cvar * 100})

var_df = pd.DataFrame(var_cvar_results)

# ==========================================
# 2. Sector HHI Concentration
# ==========================================
print("Computing Sector HHI...")
# Group by fund and sector to get sector weights
sector_weights = holdings.groupby(['amfi_code', 'sector'])['weight_pct'].sum().reset_index()
# HHI = Sum of (weight^2) - Note: weight is out of 100, so HHI is out of 10,000
sector_weights['weight_sq'] = sector_weights['weight_pct'] ** 2
hhi = sector_weights.groupby('amfi_code')['weight_sq'].sum().reset_index(name='sector_hhi')

# Merge VaR and HHI
var_cvar_report = funds[['amfi_code', 'scheme_name', 'category']].merge(var_df, on='amfi_code', how='inner')
var_cvar_report = var_cvar_report.merge(hhi, on='amfi_code', how='left')
var_cvar_report.to_csv('var_cvar_report.csv', index=False)
print("Saved var_cvar_report.csv")

# ==========================================
# 3. Rolling 90-day Sharpe
# ==========================================
print("Generating Rolling Sharpe Chart...")
rf_daily = 0.065 / 252  # 6.5% RBI repo rate proxy
key_funds = [119551, 120503, 118632, 119092, 120841] # SBI, ICICI, Nippon, Axis, Kotak Bluechip

fig = go.Figure()
colors = ['#1a73e8', '#34a853', '#ea4335', '#fbbc04', '#9c27b0']

for idx, amfi in enumerate(key_funds):
    fund_data = nav[nav['amfi_code'] == amfi].copy()
    fund_data = fund_data.set_index('date')
    
    # Rolling 90-day metrics
    roll_mean = fund_data['daily_return'].rolling(window=90).mean()
    roll_std = fund_data['daily_return'].rolling(window=90).std()
    
    # Annualised Rolling Sharpe
    roll_sharpe = ((roll_mean - rf_daily) / roll_std) * np.sqrt(252)
    fund_data['rolling_sharpe'] = roll_sharpe
    
    fund_name = funds[funds['amfi_code'] == amfi]['scheme_name'].values[0][:25]
    
    fig.add_trace(go.Scatter(x=fund_data.index, y=fund_data['rolling_sharpe'], 
                             mode='lines', name=fund_name, line=dict(color=colors[idx])))

fig.update_layout(title="Rolling 90-Day Sharpe Ratio for Key Bluechip Funds",
                  xaxis_title="Date", yaxis_title="Annualised Sharpe Ratio",
                  template="plotly_white", width=1000, height=500)
fig.write_image(os.path.join(CHART_DIR, '20_rolling_sharpe.png'))
print(f"Saved {CHART_DIR}/20_rolling_sharpe.png")

# ==========================================
# 4. Investor Cohort Analysis
# ==========================================
print("Running Investor Cohort Analysis...")
# First transaction year
first_txn = txn.groupby('investor_id')['transaction_date'].min().dt.year.reset_index()
first_txn.rename(columns={'transaction_date': 'cohort_year'}, inplace=True)
txn_cohorts = txn.merge(first_txn, on='investor_id')

cohort_summary = txn_cohorts.groupby('cohort_year').agg(
    total_invested=('amount_inr', 'sum'),
    investor_count=('investor_id', 'nunique')
).reset_index()

# Avg SIP per cohort
sip_avg = txn_cohorts[txn_cohorts['transaction_type'] == 'SIP'].groupby('cohort_year')['amount_inr'].mean().reset_index(name='avg_sip_amount')
cohort_summary = cohort_summary.merge(sip_avg, on='cohort_year', how='left')
print("Cohort Summary:")
print(cohort_summary)

# ==========================================
# 5. SIP Continuity Analysis
# ==========================================
print("Running SIP Continuity Analysis...")
sips = txn[txn['transaction_type'] == 'SIP'].sort_values(['investor_id', 'transaction_date'])
sip_counts = sips.groupby('investor_id').size()
frequent_investors = sip_counts[sip_counts >= 6].index

sip_frequent = sips[sips['investor_id'].isin(frequent_investors)].copy()
sip_frequent['days_since_last_sip'] = sip_frequent.groupby('investor_id')['transaction_date'].diff().dt.days

sip_gaps = sip_frequent.groupby('investor_id')['days_since_last_sip'].mean().reset_index()
sip_gaps['is_at_risk'] = sip_gaps['days_since_last_sip'] > 35

at_risk_count = sip_gaps['is_at_risk'].sum()
total_freq = len(sip_gaps)
print(f"SIP Continuity: Out of {total_freq} investors with 6+ SIPs, {at_risk_count} ({at_risk_count/total_freq:.1%}) are flagged as 'at-risk' (>35 days avg gap).")

print("Advanced Analytics completed successfully.")
