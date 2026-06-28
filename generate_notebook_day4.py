"""
=============================================================================
 Bluestock Fintech — Day 4: Notebook Generator
 Creates Performance_Analytics.ipynb
=============================================================================
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata.language_info = {"name": "python", "version": "3.10"}

cells = []

# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""# 📈 Bluestock Fintech — Performance Analytics

> **Day 4: Statistical Metrics & Fund Scorecard**
> **Intern:** Priyanshu Bisht | Data Analyst
> **Risk-Free Rate:** 6.5% (RBI Repo Rate proxy)

---

## Contents
1. Daily Returns & Distribution Validation
2. CAGR (1yr, 3yr, 5yr)
3. Sharpe Ratio Ranking
4. Sortino Ratio
5. Alpha & Beta (OLS vs NIFTY 100)
6. Maximum Drawdown
7. Fund Scorecard (Composite 0–100)
8. Benchmark Comparison — Top 5 vs NIFTY
"""))

# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_code_cell(
"""import os, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

warnings.filterwarnings('ignore')
%matplotlib inline

sns.set_theme(style='whitegrid', font_scale=1.15)
plt.rcParams.update({'figure.figsize':(14,8),'figure.dpi':120,'savefig.dpi':150,
    'savefig.bbox':'tight','savefig.facecolor':'white',
    'axes.titlesize':16,'axes.titleweight':'bold','axes.labelsize':13})

CHARTS = os.path.join('reports','charts')
os.makedirs(CHARTS, exist_ok=True)
RF = 0.065; RF_D = RF/252; TD = 252
PALETTE = ['#1a73e8','#34a853','#ea4335','#fbbc04','#9c27b0',
           '#00bcd4','#ff5722','#607d8b','#e91e63','#8bc34a']

def save_plotly(fig, name, w=1400, h=750):
    fig.write_html(os.path.join(CHARTS, name.replace('.png','.html')))
    try: fig.write_image(os.path.join(CHARTS, name), width=w, height=h, scale=2)
    except: pass

print('Setup complete ✅  |  Rf =', RF*100, '%')
"""))

# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_code_cell(
"""PROC = os.path.join('data','processed')
nav  = pd.read_csv(os.path.join(PROC,'02_nav_history.csv'), parse_dates=['date'])
fund = pd.read_csv(os.path.join(PROC,'01_fund_master.csv'))
perf = pd.read_csv(os.path.join(PROC,'07_scheme_performance.csv'))
bench = pd.read_csv(os.path.join(PROC,'10_benchmark_indices.csv'), parse_dates=['date'])

print(f'NAV: {len(nav):,} rows | Funds: {len(fund)} | Benchmarks: {bench[\"index_name\"].nunique()}')
"""))

# ═══════════════════════════════════════════════════════════════════════════
# 1. DAILY RETURNS
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 1. Daily Returns — Distribution Validation

**Formula:** `daily_return = NAV_t / NAV_{t-1} - 1`

We expect returns to be approximately normally distributed with slight negative skewness and fat tails (leptokurtic), which is standard for financial returns.
"""))

cells.append(nbf.v4.new_code_cell(
"""nav = nav.sort_values(['amfi_code','date'])
nav['daily_return'] = nav.groupby('amfi_code')['nav'].pct_change()

rets = nav['daily_return'].dropna()
print(f'Total observations: {len(rets):,}')
print(f'Mean:     {rets.mean():.6f}  ({rets.mean()*252:.2f}% ann.)')
print(f'Std:      {rets.std():.6f}  ({rets.std()*np.sqrt(252):.2f}% ann.)')
print(f'Skewness: {rets.skew():.4f}')
print(f'Kurtosis: {rets.kurtosis():.4f}')
print(f'Range:    {rets.min():.4f} to {rets.max():.4f}')

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
axes[0].hist(rets, bins=100, color='#1a73e8', edgecolor='white', alpha=0.8, density=True)
axes[0].axvline(rets.mean(), color='#ea4335', lw=2, label=f'Mean: {rets.mean():.5f}')
axes[0].set_title('Distribution of Daily Returns', fontsize=15, fontweight='bold')
axes[0].set_xlabel('Daily Return'); axes[0].legend(fontsize=11)

stats.probplot(rets.sample(min(5000,len(rets)), random_state=42), dist='norm', plot=axes[1])
axes[1].set_title('QQ Plot — Returns vs Normal', fontsize=15, fontweight='bold')
axes[1].get_lines()[0].set_color('#1a73e8'); axes[1].get_lines()[1].set_color('#ea4335')
plt.suptitle('Daily Return Distribution Validation', fontsize=17, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, '16_return_distribution.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# 2. CAGR
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 2. CAGR — Compound Annual Growth Rate

**Formula:** `CAGR = (NAV_end / NAV_start) ^ (1/years) - 1`
"""))

cells.append(nbf.v4.new_code_cell(
"""cagr_rows = []
for code in nav['amfi_code'].unique():
    s = nav[nav['amfi_code']==code].sort_values('date')
    nav_end, end_dt = s.iloc[-1]['nav'], s.iloc[-1]['date']
    row = {'amfi_code': code}
    for yrs, label in [(1,'cagr_1yr'),(3,'cagr_3yr'),(5,'cagr_5yr')]:
        target = end_dt - pd.DateOffset(years=yrs)
        past = s[s['date'] <= target]
        if len(past) > 0:
            nav_s = past.iloc[-1]['nav']
            ay = (end_dt - past.iloc[-1]['date']).days / 365.25
            row[label] = round(((nav_end/nav_s)**(1/ay)-1)*100, 2) if ay > 0 else None
        else:
            row[label] = None
    cagr_rows.append(row)

cagr_df = pd.DataFrame(cagr_rows).merge(fund[['amfi_code','scheme_name','sub_category','plan']], on='amfi_code')
print('Top 10 by 3-Year CAGR:')
cagr_df.nlargest(10, 'cagr_3yr')[['scheme_name','sub_category','cagr_1yr','cagr_3yr','cagr_5yr']]
"""))

# ═══════════════════════════════════════════════════════════════════════════
# 3. SHARPE
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 3. Sharpe Ratio

**Formula:** `Sharpe = (Rp - Rf) / Std(Rp) × √252`

Risk-free rate: **6.5%** (RBI repo rate proxy). Higher Sharpe = better risk-adjusted return.
"""))

cells.append(nbf.v4.new_code_cell(
"""sharpe_rows = []
for code in nav['amfi_code'].unique():
    r = nav[nav['amfi_code']==code]['daily_return'].dropna()
    if len(r) < 30: continue
    ex = r - RF_D
    sharpe = (ex.mean() / ex.std()) * np.sqrt(TD)
    sharpe_rows.append({'amfi_code':code, 'sharpe_ratio':round(sharpe,4),
        'mean_return_ann':round(r.mean()*252*100,2), 'std_ann':round(r.std()*np.sqrt(252)*100,2)})

sharpe_df = pd.DataFrame(sharpe_rows).merge(fund[['amfi_code','scheme_name','sub_category']], on='amfi_code')
sharpe_df['rank'] = sharpe_df['sharpe_ratio'].rank(ascending=False).astype(int)
sharpe_df = sharpe_df.sort_values('rank')
print('All 40 Funds — Sharpe Ranking:')
sharpe_df[['rank','scheme_name','sub_category','sharpe_ratio','mean_return_ann','std_ann']].head(15)
"""))

# ═══════════════════════════════════════════════════════════════════════════
# 4. SORTINO
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 4. Sortino Ratio

**Formula:** `Sortino = (Rp - Rf) / Downside_Std × √252`

Same as Sharpe but uses **only downside deviation** (negative return days) — better for funds with asymmetric return distributions.
"""))

cells.append(nbf.v4.new_code_cell(
"""sortino_rows = []
for code in nav['amfi_code'].unique():
    r = nav[nav['amfi_code']==code]['daily_return'].dropna()
    if len(r) < 30: continue
    ex = r - RF_D
    ds = r[r < 0]
    sortino = (ex.mean() / ds.std()) * np.sqrt(TD) if ds.std() > 0 else np.nan
    sortino_rows.append({'amfi_code':code, 'sortino_ratio':round(sortino,4),
        'downside_std_ann':round(ds.std()*np.sqrt(252)*100,2),
        'pct_negative_days':round(len(ds)/len(r)*100,1)})

sortino_df = pd.DataFrame(sortino_rows).merge(fund[['amfi_code','scheme_name']], on='amfi_code')
sortino_df['rank'] = sortino_df['sortino_ratio'].rank(ascending=False).astype(int)
sortino_df = sortino_df.sort_values('rank')
print('Top 10 — Sortino Ranking:')
sortino_df[['rank','scheme_name','sortino_ratio','downside_std_ann','pct_negative_days']].head(10)
"""))

# ═══════════════════════════════════════════════════════════════════════════
# 5. ALPHA & BETA
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 5. Alpha & Beta (OLS Regression vs NIFTY 100)

**Model:** `fund_return = α + β × benchmark_return + ε`

- **Alpha** = Jensen's Alpha (annualised) — excess return over benchmark after adjusting for risk
- **Beta** = systematic risk relative to market (1.0 = moves with market)
- Computed via `scipy.stats.linregress`
"""))

cells.append(nbf.v4.new_code_cell(
"""nifty100 = bench[bench['index_name']=='NIFTY100'].sort_values('date').copy()
nifty100['bench_return'] = nifty100['close_value'].pct_change()
nifty100 = nifty100[['date','bench_return']].dropna()

ab_rows = []
for code in nav['amfi_code'].unique():
    fr = nav[nav['amfi_code']==code][['date','daily_return']].dropna()
    m = fr.merge(nifty100, on='date', how='inner')
    if len(m) < 60: continue
    slope, intercept, r_val, p_val, _ = stats.linregress(m['bench_return'], m['daily_return'])
    ab_rows.append({'amfi_code':code, 'alpha_annual_pct':round(intercept*TD*100,2),
        'beta':round(slope,4), 'r_squared':round(r_val**2,4),
        'p_value':round(p_val,6), 'obs':len(m)})

ab_df = pd.DataFrame(ab_rows).merge(
    fund[['amfi_code','scheme_name','fund_house','sub_category','plan','expense_ratio_pct']], on='amfi_code')
ab_df = ab_df.sort_values('alpha_annual_pct', ascending=False)
ab_df.to_csv('alpha_beta.csv', index=False)
print('✅ Saved: alpha_beta.csv')
print('\\nTop 10 by Alpha:')
ab_df[['scheme_name','alpha_annual_pct','beta','r_squared','expense_ratio_pct']].head(10)
"""))

cells.append(nbf.v4.new_code_cell(
"""# Alpha-Beta Scatter
fig, ax = plt.subplots(figsize=(14, 9))
sc = ax.scatter(ab_df['beta'], ab_df['alpha_annual_pct'], c=ab_df['r_squared'],
    s=120, cmap='RdYlGn', edgecolors='white', linewidth=1.5, alpha=0.85)
plt.colorbar(sc, ax=ax, label='R-squared', shrink=0.8)

for _, r in ab_df.head(5).iterrows():
    ax.annotate(r['scheme_name'].split(' - ')[0][:20], (r['beta'], r['alpha_annual_pct']),
        fontsize=8, xytext=(5,5), textcoords='offset points')
ax.axhline(y=0, color='gray', ls='--', alpha=0.5); ax.axvline(x=1, color='gray', ls='--', alpha=0.5)
ax.set_title('Alpha vs Beta — All 40 Funds (Benchmark: NIFTY 100)\\nColor = R²',
    fontsize=17, fontweight='bold', pad=15)
ax.set_xlabel('Beta (Systematic Risk)'); ax.set_ylabel('Annual Alpha (%)')
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, '17_alpha_beta_scatter.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# 6. MAX DRAWDOWN
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 6. Maximum Drawdown

**Formula:** `Max DD = min(NAV / running_max - 1)`

Measures the worst peak-to-trough decline — the maximum loss an investor would have experienced.
"""))

cells.append(nbf.v4.new_code_cell(
"""dd_rows = []
for code in nav['amfi_code'].unique():
    s = nav[nav['amfi_code']==code].sort_values('date').copy()
    s['running_max'] = s['nav'].cummax()
    s['drawdown'] = s['nav'] / s['running_max'] - 1
    mx = s['drawdown'].min()
    mx_dt = s.loc[s['drawdown'].idxmin(), 'date']
    pk_dt = s.loc[s.loc[:s['drawdown'].idxmin(), 'nav'].idxmax(), 'date']
    pk_nav = s[s['date']==pk_dt]['nav'].values[0]
    rec = s[(s['date']>mx_dt) & (s['nav']>=pk_nav)]
    dd_rows.append({'amfi_code':code, 'max_drawdown_pct':round(mx*100,2),
        'dd_peak_date':pk_dt.strftime('%Y-%m-%d'), 'dd_trough_date':mx_dt.strftime('%Y-%m-%d'),
        'dd_days':(mx_dt-pk_dt).days, 'recovered':'Yes' if len(rec)>0 else 'No'})

dd_df = pd.DataFrame(dd_rows).merge(fund[['amfi_code','scheme_name','sub_category']], on='amfi_code')
dd_df = dd_df.sort_values('max_drawdown_pct')
print('Worst 10 Drawdowns:')
dd_df[['scheme_name','sub_category','max_drawdown_pct','dd_peak_date','dd_trough_date','dd_days','recovered']].head(10)
"""))

# ═══════════════════════════════════════════════════════════════════════════
# 7. SCORECARD
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 7. Fund Scorecard (Composite 0–100)

**Weights:**
- **30%** — 3-Year CAGR Return rank
- **25%** — Sharpe Ratio rank
- **20%** — Alpha rank
- **15%** — Expense Ratio rank (lower = better)
- **10%** — Max Drawdown rank (less severe = better)
"""))

cells.append(nbf.v4.new_code_cell(
"""sc = fund[['amfi_code','scheme_name','fund_house','sub_category','plan','expense_ratio_pct']].copy()
sc = sc.merge(cagr_df[['amfi_code','cagr_1yr','cagr_3yr','cagr_5yr']], on='amfi_code')
sc = sc.merge(sharpe_df[['amfi_code','sharpe_ratio','mean_return_ann','std_ann']], on='amfi_code')
sc = sc.merge(sortino_df[['amfi_code','sortino_ratio','downside_std_ann','pct_negative_days']], on='amfi_code')
sc = sc.merge(ab_df[['amfi_code','alpha_annual_pct','beta','r_squared']], on='amfi_code')
sc = sc.merge(dd_df[['amfi_code','max_drawdown_pct','dd_peak_date','dd_trough_date']], on='amfi_code')

n = len(sc)
sc['rk_ret'] = sc['cagr_3yr'].rank(ascending=False, na_option='bottom')
sc['rk_sh']  = sc['sharpe_ratio'].rank(ascending=False, na_option='bottom')
sc['rk_al']  = sc['alpha_annual_pct'].rank(ascending=False, na_option='bottom')
sc['rk_ex']  = sc['expense_ratio_pct'].rank(ascending=True, na_option='bottom')
sc['rk_dd']  = sc['max_drawdown_pct'].rank(ascending=False, na_option='bottom')

for c in ['rk_ret','rk_sh','rk_al','rk_ex','rk_dd']:
    sc[c+'_s'] = ((n - sc[c] + 1) / n * 100).round(1)

sc['composite_score'] = (0.30*sc['rk_ret_s'] + 0.25*sc['rk_sh_s'] + 0.20*sc['rk_al_s'] +
                         0.15*sc['rk_ex_s'] + 0.10*sc['rk_dd_s']).round(1)
sc['overall_rank'] = sc['composite_score'].rank(ascending=False).astype(int)
sc = sc.sort_values('overall_rank')

out_cols = ['overall_rank','amfi_code','scheme_name','fund_house','sub_category','plan',
    'composite_score','cagr_1yr','cagr_3yr','cagr_5yr','sharpe_ratio','sortino_ratio',
    'alpha_annual_pct','beta','r_squared','max_drawdown_pct','expense_ratio_pct',
    'mean_return_ann','std_ann','downside_std_ann','pct_negative_days','dd_peak_date','dd_trough_date']
sc_out = sc[[c for c in out_cols if c in sc.columns]]
sc_out.to_csv('fund_scorecard.csv', index=False)
print('✅ Saved: fund_scorecard.csv')
print(f'\\nTop 15 Fund Scorecard:')
sc_out[['overall_rank','scheme_name','composite_score','cagr_3yr','sharpe_ratio','alpha_annual_pct','max_drawdown_pct']].head(15)
"""))

cells.append(nbf.v4.new_code_cell(
"""# Scorecard Bar Chart
top20 = sc_out.head(20).copy()
top20['short'] = top20['scheme_name'].apply(lambda x: x.split(' - ')[0][:30])

fig, ax = plt.subplots(figsize=(16, 10))
colors = ['#ea4335' if i<3 else '#34a853' if i<5 else '#1a73e8' for i in range(len(top20))]
colors.reverse()
bars = ax.barh(top20['short'][::-1], top20['composite_score'][::-1], color=colors, edgecolor='white', lw=1.5)
for bar, s in zip(bars, top20['composite_score'][::-1]):
    ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2, f'{s:.1f}', va='center', fontsize=10, fontweight='bold')
ax.set_title('Fund Scorecard — Top 20 (Composite Score 0–100)\\n30% Return + 25% Sharpe + 20% Alpha + 15% Expense + 10% DD',
    fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Composite Score'); ax.set_xlim(0, 105)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, '18_fund_scorecard.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# 8. BENCHMARK COMPARISON
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 8. Benchmark Comparison — Top 5 Funds vs NIFTY

**Tracking Error** = `Std(fund_return - benchmark_return) × √252`

A lower tracking error means the fund closely follows its benchmark.
"""))

cells.append(nbf.v4.new_code_cell(
"""# Get top 5 equity funds
eq = sc_out.merge(fund[['amfi_code','category']], on='amfi_code')
eq = eq[eq['category']=='Equity']
top5 = eq.head(5)
latest = nav['date'].max()
start_3y = latest - pd.DateOffset(years=3)

fig, ax = plt.subplots(figsize=(16, 9))
ci = 0
fund_ret_dict = {}
for _, row in top5.iterrows():
    s = nav[(nav['amfi_code']==row['amfi_code']) & (nav['date']>=start_3y)].sort_values('date')
    if len(s)==0: continue
    rebased = s['nav'] / s['nav'].iloc[0] * 100
    short = row['scheme_name'].split(' - ')[0][:25]
    ax.plot(s['date'], rebased, label=short, color=PALETTE[ci], lw=2)
    fund_ret_dict[row['amfi_code']] = s.set_index('date')['daily_return']
    ci += 1

for idx_name, ls, c in [('NIFTY50','--','#202124'), ('NIFTY100',':','#607d8b')]:
    idx = bench[(bench['index_name']==idx_name) & (bench['date']>=start_3y)].sort_values('date')
    rebased = idx['close_value'] / idx['close_value'].iloc[0] * 100
    ax.plot(idx['date'], rebased, label=idx_name, color=c, lw=3, ls=ls)

ax.set_title('Top 5 Equity Funds vs NIFTY 50 & NIFTY 100 — 3-Year (Rebased to 100)',
    fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Date'); ax.set_ylabel('Rebased Value (100 = Start)')
ax.legend(fontsize=10, loc='upper left')
ax.axhline(y=100, color='gray', ls='-', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, '19_benchmark_comparison.png'), dpi=150, bbox_inches='tight')
plt.show()

# Tracking Error
nifty100_r = bench[bench['index_name']=='NIFTY100'].sort_values('date').copy()
nifty100_r['br'] = nifty100_r['close_value'].pct_change()
br = nifty100_r[nifty100_r['date']>=start_3y].set_index('date')['br']

print('\\nTracking Error (vs NIFTY 100):')
for _, row in top5.iterrows():
    if row['amfi_code'] not in fund_ret_dict: continue
    m = pd.DataFrame({'f':fund_ret_dict[row['amfi_code']], 'b':br}).dropna()
    te = (m['f']-m['b']).std() * np.sqrt(252)
    print(f"  {row['scheme_name'].split(' - ')[0][:40]:<42} TE: {te*100:.2f}%")
"""))

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 📋 Summary

### Deliverables
| File | Description |
|------|-------------|
| `fund_scorecard.csv` | Composite ranked scorecard for all 40 funds (0–100) |
| `alpha_beta.csv` | Alpha, Beta, R² for all funds vs NIFTY 100 |
| `reports/charts/16_return_distribution.png` | Daily return distribution + QQ plot |
| `reports/charts/17_alpha_beta_scatter.png` | Alpha vs Beta scatter (colour = R²) |
| `reports/charts/18_fund_scorecard.png` | Top 20 funds bar chart |
| `reports/charts/19_benchmark_comparison.png` | Top 5 vs NIFTY 50 & NIFTY 100 |

### Key Metrics Computed
- **Daily Returns** — validated for reasonable distribution (skewness, kurtosis, QQ plot)
- **CAGR** — 1-year, 3-year, 5-year compound annual growth rates
- **Sharpe Ratio** — risk-adjusted return using total standard deviation (Rf = 6.5%)
- **Sortino Ratio** — risk-adjusted return using downside deviation only
- **Alpha & Beta** — OLS regression against NIFTY 100 benchmark
- **Max Drawdown** — worst peak-to-trough decline with date ranges
- **Fund Scorecard** — weighted composite (30% Return + 25% Sharpe + 20% Alpha + 15% Expense + 10% DD)
- **Tracking Error** — annualised standard deviation of excess returns vs benchmark
"""))

# ═══════════════════════════════════════════════════════════════════════════
nb.cells = cells
with open("Performance_Analytics.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Performance_Analytics.ipynb created!")
print(f"Cells: {len(cells)} ({sum(1 for c in cells if c.cell_type=='markdown')} markdown + {sum(1 for c in cells if c.cell_type=='code')} code)")
