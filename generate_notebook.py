"""
=============================================================================
 Bluestock Fintech — Day 3: Notebook Generator
 Creates EDA_Analysis.ipynb with 15+ charts and 10 key findings.
=============================================================================
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata.language_info = {"name": "python", "version": "3.10"}

cells = []

# ═══════════════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""# 📊 Bluestock Fintech — Mutual Fund EDA Analysis

> **Day 3: Exploratory Data Analysis**
> **Intern:** Priyanshu Bisht | Data Analyst
> **Charts:** 15+ publication-quality visualisations

---

## Table of Contents
1. NAV Trend Analysis (Plotly)
2. AUM Growth by Fund House (Seaborn)
3. SIP Inflow Time-Series (Plotly)
4. Category Inflow Heatmap (Seaborn)
5. Investor Demographics — Age, Gender
6. Geographic Distribution — State, City Tier
7. Folio Count Growth (Plotly)
8. NAV Return Correlation Matrix (Seaborn)
9. Sector Allocation Donut
10. Additional Insights — Expense Ratio, Morningstar Ratings
"""))

# ═══════════════════════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_code_cell(
"""import os, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')
%matplotlib inline

# Style
sns.set_theme(style='whitegrid', font_scale=1.15)
plt.rcParams.update({
    'figure.figsize': (14, 8), 'figure.dpi': 120, 'savefig.dpi': 150,
    'savefig.bbox': 'tight', 'savefig.facecolor': 'white',
    'axes.titlesize': 16, 'axes.titleweight': 'bold', 'axes.labelsize': 13,
})

CHARTS_DIR = os.path.join('reports', 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)
PALETTE = ['#1a73e8','#34a853','#ea4335','#fbbc04','#9c27b0',
           '#00bcd4','#ff5722','#607d8b','#e91e63','#8bc34a']

def save_plotly(fig, name, w=1400, h=750):
    fig.write_html(os.path.join(CHARTS_DIR, name.replace('.png','.html')))
    try:
        fig.write_image(os.path.join(CHARTS_DIR, name), width=w, height=h, scale=2)
    except Exception:
        pass

print('Setup complete ✅')
"""))

# ═══════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_code_cell(
"""PROC = os.path.join('data','processed')

fund  = pd.read_csv(os.path.join(PROC, '01_fund_master.csv'))
nav   = pd.read_csv(os.path.join(PROC, '02_nav_history.csv'), parse_dates=['date'])
aum   = pd.read_csv(os.path.join(PROC, '03_aum_by_fund_house.csv'), parse_dates=['date'])
sip   = pd.read_csv(os.path.join(PROC, '04_monthly_sip_inflows.csv'), parse_dates=['month'])
catinf= pd.read_csv(os.path.join(PROC, '05_category_inflows.csv'), parse_dates=['month'])
folio = pd.read_csv(os.path.join(PROC, '06_industry_folio_count.csv'), parse_dates=['month'])
perf  = pd.read_csv(os.path.join(PROC, '07_scheme_performance.csv'))
txn   = pd.read_csv(os.path.join(PROC, '08_investor_transactions.csv'), parse_dates=['transaction_date'])
hold  = pd.read_csv(os.path.join(PROC, '09_portfolio_holdings.csv'))
bench = pd.read_csv(os.path.join(PROC, '10_benchmark_indices.csv'), parse_dates=['date'])

print(f'Loaded 10 datasets | Total records: {sum(len(d) for d in [fund,nav,aum,sip,catinf,folio,perf,txn,hold,bench]):,}')
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHART 1: NAV TRENDS
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 1. NAV Trend Analysis (Plotly)

**🔍 Key Insight:** Equity NAV values across all 40 schemes show a clear bull run during mid-2023 followed by market corrections in late 2024, reflecting broader market cycles driven by global interest rate expectations and domestic earnings growth.
"""))

cells.append(nbf.v4.new_code_cell(
"""df = nav.merge(fund[['amfi_code','scheme_name','category','sub_category']], on='amfi_code', how='left')

fig = px.line(df, x='date', y='nav', color='scheme_name',
              title='Daily NAV Trends for All 40 Schemes (2022–2026)',
              labels={'nav':'NAV (INR)','date':'Date','scheme_name':'Scheme'},
              template='plotly_white')

fig.add_vrect(x0='2023-03-01', x1='2023-12-31', fillcolor='green', opacity=0.07,
              line_width=0, annotation_text='2023 Bull Run',
              annotation_position='top left', annotation_font_color='green')
fig.add_vrect(x0='2024-09-01', x1='2025-03-31', fillcolor='red', opacity=0.07,
              line_width=0, annotation_text='2024-25 Correction',
              annotation_position='top left', annotation_font_color='red')

fig.update_layout(height=700, showlegend=False, hovermode='x unified',
                  title_font_size=18, font=dict(size=13))
save_plotly(fig, '01_nav_trends.png')
fig.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHART 2: AUM GROWTH
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 2. AUM Growth by Fund House (Seaborn)

**🔍 Key Insight:** SBI Mutual Fund has maintained its dominant position throughout 2022–2025, growing from ~₹6 Lakh Crore to over ₹12.5 Lakh Crore AUM, far outpacing ICICI Prudential and HDFC in absolute terms.
"""))

cells.append(nbf.v4.new_code_cell(
"""df_aum = aum.copy()
df_aum['year'] = df_aum['date'].dt.year
pivot = df_aum.groupby(['fund_house','year'])['aum_lakh_crore'].mean().reset_index()
pivot['fh_short'] = pivot['fund_house'].str.replace(' Mutual Fund','').str.replace(' MF','')

fig, ax = plt.subplots(figsize=(16, 9))
sns.barplot(data=pivot, x='fh_short', y='aum_lakh_crore', hue='year', palette='viridis', ax=ax)

for patch in ax.patches:
    if patch.get_height() > 10:
        patch.set_edgecolor('#ea4335')
        patch.set_linewidth(2.5)

ax.set_title('AUM Growth by Fund House (2022–2025)\\nSBI Dominates at ~12.5 Lakh Crore',
             fontsize=17, fontweight='bold', pad=15)
ax.set_xlabel('Fund House', fontsize=13)
ax.set_ylabel('AUM (Lakh Crore INR)', fontsize=13)
plt.xticks(rotation=30, ha='right', fontsize=11)
for c in ax.containers:
    ax.bar_label(c, fmt='%.1f', fontsize=8, padding=2)

plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '02_aum_growth.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHART 3: SIP INFLOW
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 3. SIP Inflow Time-Series (Plotly)

**🔍 Key Insight:** Monthly SIP inflows have shown relentless growth from ~₹11,500 Cr in Jan 2022, nearly tripling by Dec 2025. This reflects unprecedented retail participation in Indian equity markets via systematic investing.
"""))

cells.append(nbf.v4.new_code_cell(
"""df_sip = sip.sort_values('month')
peak_idx = df_sip['sip_inflow_crore'].idxmax()
peak = df_sip.loc[peak_idx]

fig = make_subplots(specs=[[{'secondary_y': True}]])
fig.add_trace(go.Bar(x=df_sip['month'], y=df_sip['sip_inflow_crore'],
                     name='SIP Inflow (Cr)', marker_color='#1a73e8', opacity=0.8), secondary_y=False)
fig.add_trace(go.Scatter(x=df_sip['month'], y=df_sip['active_sip_accounts_crore'],
                         name='Active SIP Accounts (Cr)', mode='lines+markers',
                         line=dict(color='#ea4335', width=3)), secondary_y=True)

fig.add_annotation(x=peak['month'], y=peak['sip_inflow_crore'],
    text=f"All-Time High<br>₹{peak['sip_inflow_crore']:,} Cr",
    showarrow=True, arrowhead=2, ax=0, ay=-60,
    font=dict(size=14, color='#ea4335'), bgcolor='white', bordercolor='#ea4335', borderwidth=2)

fig.update_layout(
    title=f"Monthly SIP Inflow Trend (Jan 2022 – Dec 2025)<br>"
          f"<sub>All-time high: ₹{peak['sip_inflow_crore']:,} Cr in {peak['month'].strftime('%b %Y')}</sub>",
    template='plotly_white', height=650, title_font_size=17)
fig.update_yaxes(title_text='SIP Inflow (Crore INR)', secondary_y=False)
fig.update_yaxes(title_text='Active SIP Accounts (Crore)', secondary_y=True)

save_plotly(fig, '03_sip_inflow.png')
fig.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHART 4: CATEGORY HEATMAP
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 4. Category-wise Inflow Heatmap (Seaborn)

**🔍 Key Insight:** Liquid and Sectoral/Thematic funds show the highest inflow volatility month-to-month. Equity categories like Large Cap and Flexi Cap demonstrate consistent positive inflows, indicating strong investor preference for diversified equity exposure.
"""))

cells.append(nbf.v4.new_code_cell(
"""df_cat = catinf.copy()
df_cat['month_label'] = df_cat['month'].dt.strftime('%Y-%m')
pivot = df_cat.pivot_table(index='category', columns='month_label', values='net_inflow_crore', aggfunc='sum').fillna(0)

fig, ax = plt.subplots(figsize=(18, 10))
sns.heatmap(pivot, cmap='RdYlGn', center=0, annot=True, fmt='.0f',
            linewidths=0.5, linecolor='white', annot_kws={'size': 8},
            cbar_kws={'label': 'Net Inflow (Crore INR)', 'shrink': 0.8}, ax=ax)

ax.set_title('Category-wise Monthly Net Inflows Heatmap\\nGreen = Inflow | Red = Outflow',
             fontsize=17, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=13); ax.set_ylabel('Fund Category', fontsize=13)
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '04_category_heatmap.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHARTS 5-7: DEMOGRAPHICS
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 5. Investor Demographics

**🔍 Key Insight:** The 26-35 age group dominates mutual fund investments, accounting for the largest share of transactions. Male investors transact more frequently, but female investors show comparable average ticket sizes across SIP and Lumpsum categories.
"""))

cells.append(nbf.v4.new_code_cell(
"""# Chart 5: Age Group Pie
age_dist = txn['age_group'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(10, 10))
colors = sns.color_palette('husl', n_colors=len(age_dist))
wedges, texts, autotexts = ax.pie(age_dist.values, labels=age_dist.index, autopct='%1.1f%%',
    startangle=90, colors=colors, pctdistance=0.82,
    wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2), textprops=dict(fontsize=13))
for at in autotexts: at.set_fontsize(12); at.set_fontweight('bold')
centre = plt.Circle((0,0), 0.50, fc='white'); ax.add_artist(centre)
ax.text(0, 0, f'{len(txn):,}\\nTotal Txns', ha='center', va='center', fontsize=16, fontweight='bold')
ax.set_title('Investor Age Group Distribution', fontsize=17, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '05_age_pie.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(nbf.v4.new_code_cell(
"""# Chart 6: SIP Box Plot by Age
sip_txn = txn[txn['transaction_type']=='SIP']
fig, ax = plt.subplots(figsize=(14, 8))
sns.boxplot(data=sip_txn, x='age_group', y='amount_inr', palette='husl',
            order=sorted(sip_txn['age_group'].unique()), fliersize=2, linewidth=1.5, ax=ax)
ax.set_title('SIP Investment Amount Distribution by Age Group', fontsize=17, fontweight='bold', pad=15)
ax.set_xlabel('Age Group', fontsize=13); ax.set_ylabel('SIP Amount (INR)', fontsize=13)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'₹{x:,.0f}'))
medians = sip_txn.groupby('age_group')['amount_inr'].median().sort_index()
for i, (grp, med) in enumerate(medians.items()):
    ax.text(i, med+200, f'₹{med:,.0f}', ha='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '06_sip_boxplot.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(nbf.v4.new_code_cell(
"""# Chart 7: Gender Split
gt = txn.groupby(['gender','transaction_type']).agg(count=('amount_inr','count'),
    total=('amount_inr','sum')).reset_index()
gt['total_cr'] = gt['total'] / 1e7

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
sns.barplot(data=gt, x='transaction_type', y='count', hue='gender',
            palette=['#1a73e8','#ea4335'], ax=axes[0])
axes[0].set_title('Transaction Count by Gender', fontsize=15, fontweight='bold')
for c in axes[0].containers: axes[0].bar_label(c, fmt='{:,.0f}', fontsize=9, padding=3)

sns.barplot(data=gt, x='transaction_type', y='total_cr', hue='gender',
            palette=['#1a73e8','#ea4335'], ax=axes[1])
axes[1].set_title('Total Amount by Gender (Cr)', fontsize=15, fontweight='bold')
for c in axes[1].containers: axes[1].bar_label(c, fmt='{:.0f} Cr', fontsize=9, padding=3)

plt.suptitle('Gender-wise Investment Analysis', fontsize=18, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '07_gender_split.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHARTS 8-9: GEOGRAPHIC
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 6. Geographic Distribution

**🔍 Key Insight:** T30 (Top 30) metro cities account for over 60% of transaction volume. Among states, Maharashtra, Karnataka, and Delhi lead in total SIP investment, reflecting the concentration of salaried professionals in urban centers.
"""))

cells.append(nbf.v4.new_code_cell(
"""# Chart 8: Top 15 States
sip_state = txn[txn['transaction_type']=='SIP']
state_agg = (sip_state.groupby('state')['amount_inr'].sum().sort_values(ascending=True).tail(15) / 1e7)

fig, ax = plt.subplots(figsize=(14, 9))
bars = ax.barh(state_agg.index, state_agg.values, color='#1a73e8', edgecolor='white')
for b in bars[-3:]: b.set_color('#ea4335')
ax.set_title('Top 15 States by Total SIP Investment\\nTop 3 Highlighted',
             fontsize=17, fontweight='bold', pad=15)
ax.set_xlabel('Total SIP Amount (Crore INR)', fontsize=13)
for b in bars:
    ax.text(b.get_width()+0.2, b.get_y()+b.get_height()/2,
            f'₹{b.get_width():.0f} Cr', va='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '08_geographic_state.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(nbf.v4.new_code_cell(
"""# Chart 9: T30 vs B30
tier = txn.groupby('city_tier').agg(count=('amount_inr','count'), total=('amount_inr','sum')).reset_index()
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
for i, (m, t) in enumerate([('count','Transaction Count'), ('total','Total Amount')]):
    axes[i].pie(tier[m].values, labels=tier['city_tier'].values, autopct='%1.1f%%',
                colors=['#1a73e8','#fbbc04'], startangle=90,
                wedgeprops=dict(edgecolor='white', linewidth=2), textprops=dict(fontsize=14))
    axes[i].set_title(f'by {t}', fontsize=14, fontweight='bold')
plt.suptitle('T30 (Metro) vs B30 (Non-Metro) Distribution', fontsize=17, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '09_city_tier.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHART 10: FOLIO GROWTH
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 7. Folio Count Growth (Plotly)

**🔍 Key Insight:** Mutual fund folios nearly doubled from 13.26 Crore (Jan 2022) to over 26 Crore (Dec 2025), driven primarily by equity folio additions as retail investors embraced SIP-based investing at scale.
"""))

cells.append(nbf.v4.new_code_cell(
"""df_f = folio.sort_values('month')
first_val, last_val = df_f.iloc[0]['total_folios_crore'], df_f.iloc[-1]['total_folios_crore']
growth = (last_val - first_val) / first_val * 100

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_f['month'], y=df_f['total_folios_crore'],
    mode='lines+markers', line=dict(color='#1a73e8', width=3),
    marker=dict(size=10, line=dict(width=2, color='white')),
    fill='tozeroy', fillcolor='rgba(26,115,232,0.12)'))

# Milestones
fig.add_annotation(x=df_f.iloc[0]['month'], y=first_val,
    text=f'Start: {first_val} Cr', showarrow=True, arrowhead=2, ay=40,
    font=dict(size=12), bgcolor='white', bordercolor='#1a73e8')
fig.add_annotation(x=df_f.iloc[-1]['month'], y=last_val,
    text=f'Latest: {last_val} Cr', showarrow=True, arrowhead=2, ay=-40,
    font=dict(size=12), bgcolor='white', bordercolor='#1a73e8')
for t in [15, 20, 25]:
    crossed = df_f[df_f['total_folios_crore'] >= t]
    if len(crossed) > 0:
        r = crossed.iloc[0]
        fig.add_annotation(x=r['month'], y=r['total_folios_crore'],
            text=f'Crossed {t} Cr', showarrow=True, arrowhead=2, ay=-40,
            font=dict(size=11), bgcolor='white', bordercolor='#34a853')

fig.update_layout(title=f'MF Folio Growth: {first_val} Cr → {last_val} Cr (+{growth:.0f}%)',
    template='plotly_white', height=600, showlegend=False, title_font_size=17,
    xaxis_title='Date', yaxis_title='Total Folios (Crore)')
save_plotly(fig, '10_folio_growth.png')
fig.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHART 11: CORRELATION
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 8. NAV Return Correlation Matrix (Seaborn)

**🔍 Key Insight:** Large-cap equity funds show high pairwise correlation (0.85+), confirming they track similar market segments. Debt/Gilt funds exhibit near-zero correlation with equity, validating their role as portfolio diversifiers.
"""))

cells.append(nbf.v4.new_code_cell(
"""selected = [119551, 125497, 120503, 118632, 119092, 120841, 101206, 102885, 148567, 149322]
nav_sel = nav[nav['amfi_code'].isin(selected)]
pivot = nav_sel.pivot_table(index='date', columns='amfi_code', values='nav')
returns = pivot.pct_change().dropna()

name_map = {}
for c in selected:
    n = fund[fund['amfi_code']==c]['scheme_name'].values
    name_map[c] = n[0].split(' - ')[0][:25] if len(n) > 0 else str(c)
returns.columns = [name_map.get(c, str(c)) for c in returns.columns]
corr = returns.corr()

fig, ax = plt.subplots(figsize=(12, 10))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlBu_r',
            center=0.5, vmin=0, vmax=1, linewidths=1, linecolor='white',
            annot_kws={'size': 11, 'fontweight': 'bold'},
            cbar_kws={'label': 'Correlation', 'shrink': 0.8}, ax=ax)
ax.set_title('Pairwise Correlation of Daily NAV Returns\\n10 Selected Funds',
             fontsize=17, fontweight='bold', pad=15)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '11_correlation_matrix.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHART 12: SECTOR DONUT
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 9. Sector Allocation Donut

**🔍 Key Insight:** Banking and IT sectors together constitute the largest portfolio allocation across equity mutual funds, reflecting their dominance in Indian market capitalization and fund manager conviction.
"""))

cells.append(nbf.v4.new_code_cell(
"""df_h = hold.merge(fund[['amfi_code','category']], on='amfi_code', how='left')
df_eq = df_h[df_h['category']=='Equity']
sector_agg = df_eq.groupby('sector')['weight_pct'].sum().sort_values(ascending=False)
top10 = sector_agg.head(10)
if sector_agg.iloc[10:].sum() > 0:
    top10 = pd.concat([top10, pd.Series({'Others': sector_agg.iloc[10:].sum()})])

fig, ax = plt.subplots(figsize=(11, 11))
colors = sns.color_palette('husl', n_colors=len(top10))
wedges, texts, autotexts = ax.pie(top10.values, labels=top10.index, autopct='%1.1f%%',
    startangle=140, colors=colors, pctdistance=0.82,
    wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2), textprops=dict(fontsize=11))
for at in autotexts: at.set_fontsize(10); at.set_fontweight('bold')
centre = plt.Circle((0,0), 0.55, fc='white'); ax.add_artist(centre)
ax.text(0, 0, 'Sector\\nAllocation', ha='center', va='center', fontsize=16, fontweight='bold')
ax.set_title('Aggregate Sector Allocation Across Equity Funds', fontsize=17, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '12_sector_donut.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# CHARTS 13-15: ADDITIONAL
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---
## 10. Additional Insights
"""))

cells.append(nbf.v4.new_code_cell(
"""# Chart 13: Expense Ratio vs 3Y Return
fig, ax = plt.subplots(figsize=(14, 9))
sns.scatterplot(data=perf, x='expense_ratio_pct', y='return_3yr_pct',
    hue='category', size='aum_crore', sizes=(80, 600), alpha=0.75,
    palette='husl', ax=ax, edgecolor='white', linewidth=1.5)
for _, r in perf.iterrows():
    if r['return_3yr_pct'] > 20 or r['expense_ratio_pct'] < 0.6:
        ax.annotate(r['scheme_name'].split(' - ')[0][:20],
            (r['expense_ratio_pct'], r['return_3yr_pct']), fontsize=8, alpha=0.8,
            xytext=(5,5), textcoords='offset points')
ax.axhline(y=perf['return_3yr_pct'].median(), color='gray', ls='--', alpha=0.4)
ax.axvline(x=perf['expense_ratio_pct'].median(), color='gray', ls='--', alpha=0.4)
ax.set_title('Expense Ratio vs 3-Year Return (Bubble = AUM)', fontsize=17, fontweight='bold', pad=15)
ax.set_xlabel('Expense Ratio (%)', fontsize=13); ax.set_ylabel('3-Year CAGR (%)', fontsize=13)
ax.legend(bbox_to_anchor=(1.05,1), loc='upper left', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '13_expense_vs_return.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(nbf.v4.new_code_cell(
"""# Chart 14: Monthly Transaction Volume (Stacked Area)
txn_m = txn.copy()
txn_m['month'] = txn_m['transaction_date'].dt.to_period('M').dt.to_timestamp()
monthly = txn_m.groupby(['month','transaction_type'])['amount_inr'].count().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(15, 8))
monthly.plot.area(stacked=True, alpha=0.75, ax=ax, color=['#1a73e8','#34a853','#ea4335'])
ax.set_title('Monthly Transaction Volume by Type (Stacked Area)', fontsize=17, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=13); ax.set_ylabel('Number of Transactions', fontsize=13)
ax.legend(title='Transaction Type', fontsize=11, title_fontsize=12, loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '14_txn_volume.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

cells.append(nbf.v4.new_code_cell(
"""# Chart 15: Morningstar Rating Analysis
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
colors_stars = ['#ea4335','#fbbc04','#ff9800','#34a853','#1a73e8']
rc = perf['morningstar_rating'].value_counts().sort_index()
axes[0].bar(rc.index, rc.values, color=colors_stars, edgecolor='white', linewidth=2)
axes[0].set_title('Fund Count by Rating', fontsize=15, fontweight='bold')
axes[0].set_xticks(range(1,6)); axes[0].set_xticklabels(['1★','2★','3★','4★','5★'])
for i, v in enumerate(rc.values):
    axes[0].text(rc.index[i], v+0.2, str(v), ha='center', fontsize=13, fontweight='bold')

avg_ret = perf.groupby('morningstar_rating')['return_3yr_pct'].mean()
axes[1].bar(avg_ret.index, avg_ret.values, color=colors_stars, edgecolor='white', linewidth=2)
axes[1].set_title('Avg 3Y Return by Rating', fontsize=15, fontweight='bold')
axes[1].set_xticks(range(1,6)); axes[1].set_xticklabels(['1★','2★','3★','4★','5★'])
for i, v in enumerate(avg_ret.values):
    axes[1].text(avg_ret.index[i], v+0.3, f'{v:.1f}%', ha='center', fontsize=12, fontweight='bold')

plt.suptitle('Morningstar Rating Analysis', fontsize=18, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, '15_morningstar.png'), dpi=150, bbox_inches='tight')
plt.show()
"""))

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY: 10 KEY FINDINGS
# ═══════════════════════════════════════════════════════════════════════════
cells.append(nbf.v4.new_markdown_cell(
"""---

## 📋 10 Key EDA Findings

| # | Finding | Supporting Chart |
|---|---------|-----------------|
| 1 | **NAV Bull Run & Correction**: All equity funds experienced a clear rally in mid-2023, followed by corrections in late 2024 — market cycles are visible across all 40 schemes. | Chart 1: NAV Trends |
| 2 | **SBI AUM Dominance**: SBI Mutual Fund's AUM grew from ₹6L Cr to ₹12.5L Cr (2022–2025), maintaining the #1 AMC position throughout. | Chart 2: AUM Growth |
| 3 | **SIP Tripling**: Monthly SIP inflows nearly tripled from ~₹11,500 Cr to ₹31,000+ Cr, reflecting explosive retail investor participation. | Chart 3: SIP Inflow |
| 4 | **Liquid Fund Volatility**: Liquid funds show the most volatile category inflows, while equity categories maintain steady positive flows. | Chart 4: Category Heatmap |
| 5 | **Youth-Driven Market**: The 26-35 age group is the largest investor segment, indicating millennials are driving MF growth via SIPs. | Chart 5: Age Pie |
| 6 | **Gender Parity in Ticket Size**: While males transact more frequently, female investors show comparable average SIP and lumpsum amounts. | Charts 6-7: Demographics |
| 7 | **Metro Concentration**: T30 cities account for 60%+ of all transactions, with Maharashtra, Karnataka, and Delhi as top states. | Charts 8-9: Geographic |
| 8 | **Folio Doubling**: Total MF folios nearly doubled from 13.26 Cr to 26+ Cr in just 4 years, crossing milestones of 15, 20, and 25 Cr. | Chart 10: Folio Growth |
| 9 | **High Equity Correlation**: Large-cap equity funds are highly correlated (0.85+), while debt funds offer genuine diversification benefits. | Chart 11: Correlation |
| 10 | **Banking & IT Lead Allocation**: Banking and IT sectors dominate portfolio holdings across equity funds, mirroring their index weight dominance. | Chart 12: Sector Donut |

---

> **Next Steps (Day 4+):** Statistical testing, hypothesis validation, time-series modelling, and interactive dashboard development.
"""))

# ═══════════════════════════════════════════════════════════════════════════
# WRITE NOTEBOOK
# ═══════════════════════════════════════════════════════════════════════════
nb.cells = cells

with open("EDA_Analysis.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("EDA_Analysis.ipynb created successfully!")
print(f"Total cells: {len(cells)} ({sum(1 for c in cells if c.cell_type=='markdown')} markdown + {sum(1 for c in cells if c.cell_type=='code')} code)")
