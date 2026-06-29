"""
=============================================================================
 Bluestock Fintech — Dashboard Deliverables Generator
 Creates the 4 PNG dashboard page mockups and compiles them into Dashboard.pdf
=============================================================================
"""
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

DASH_DIR = "dashboard"
os.makedirs(DASH_DIR, exist_ok=True)
PROC = os.path.join("data", "processed")

# Colors
BGC = "#f4f6f9"
PANEL = "#ffffff"
TEXT = "#202124"
BLUE = "#1a73e8"
GREEN = "#34a853"
RED = "#ea4335"
YELLOW = "#fbbc04"

# ---------------------------------------------------------------------------
# Load Data
# ---------------------------------------------------------------------------
fund = pd.read_csv(os.path.join(PROC, '01_fund_master.csv'))
nav = pd.read_csv(os.path.join(PROC, '02_nav_history.csv'), parse_dates=['date'])
aum = pd.read_csv(os.path.join(PROC, '03_aum_by_fund_house.csv'), parse_dates=['date'])
perf = pd.read_csv(os.path.join(PROC, '07_scheme_performance.csv'))
sip = pd.read_csv(os.path.join(PROC, '04_monthly_sip_inflows.csv'), parse_dates=['month'])
cat = pd.read_csv(os.path.join(PROC, '05_category_inflows.csv'), parse_dates=['month'])
folio = pd.read_csv(os.path.join(PROC, '06_industry_folio_count.csv'), parse_dates=['month'])
txn = pd.read_csv(os.path.join(PROC, '08_investor_transactions.csv'), parse_dates=['transaction_date'])
bench = pd.read_csv(os.path.join(PROC, '10_benchmark_indices.csv'), parse_dates=['date'])
score = pd.read_csv('fund_scorecard.csv')

def save_fig(fig, name):
    path = os.path.join(DASH_DIR, name)
    fig.write_image(path, width=1600, height=900, scale=1.5)
    print(f"Saved: {path}")

# ===========================================================================
# PAGE 1: INDUSTRY OVERVIEW
# ===========================================================================
def build_page1():
    print("Building Page 1: Industry Overview...")
    fig = make_subplots(
        rows=2, cols=4,
        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
               [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None]],
        row_heights=[0.25, 0.75],
        vertical_spacing=0.1,
        subplot_titles=("", "", "", "", "Industry AUM Trend (2022–2025)", "AUM by Top AMC")
    )

    # KPIs
    latest_aum = aum[aum['date'] == aum['date'].max()]['aum_crore'].sum()
    total_sip = sip['sip_inflow_crore'].sum()
    latest_folio = folio[folio['month'] == folio['month'].max()]['total_folios_crore'].sum()
    total_schemes = 1908  # Hardcoded from prompt requirement

    fig.add_trace(go.Indicator(mode="number", value=latest_aum / 100000, number={'prefix': "₹", 'suffix': "L Cr", "valueformat": ".1f"}, title={"text": "Total Industry AUM"}), row=1, col=1)
    fig.add_trace(go.Indicator(mode="number", value=total_sip / 1000, number={'prefix': "₹", 'suffix': "K Cr", "valueformat": ".1f"}, title={"text": "Total SIP Inflows (2022-25)"}), row=1, col=2)
    fig.add_trace(go.Indicator(mode="number", value=latest_folio, number={'suffix': " Cr", "valueformat": ".2f"}, title={"text": "Total Folios"}), row=1, col=3)
    fig.add_trace(go.Indicator(mode="number", value=total_schemes, number={'valueformat': ","}, title={"text": "Total Schemes"}), row=1, col=4)

    # Line Chart: AUM Trend
    aum_trend = aum.groupby('date')['aum_crore'].sum().reset_index()
    fig.add_trace(go.Scatter(x=aum_trend['date'], y=aum_trend['aum_crore'], mode='lines+markers', line=dict(color=BLUE, width=3), name='Total AUM'), row=2, col=1)

    # Bar Chart: AUM by AMC
    latest_q = aum['date'].max()
    amc_aum = aum[aum['date'] == latest_q].groupby('fund_house')['aum_crore'].sum().nlargest(10).reset_index()
    fig.add_trace(go.Bar(x=amc_aum['fund_house'].str[:15], y=amc_aum['aum_crore'], marker_color=GREEN, name='AUM by AMC'), row=2, col=3)

    fig.update_layout(title_text="<b>Bluestock Mutual Fund Dashboard | Page 1: Industry Overview</b>", title_font_size=24,
                      plot_bgcolor=PANEL, paper_bgcolor=BGC, font=dict(color=TEXT), showlegend=False,
                      margin=dict(t=100, b=50, l=50, r=50))
    save_fig(fig, "dashboard_page1_industry.png")

# ===========================================================================
# PAGE 2: FUND PERFORMANCE
# ===========================================================================
def build_page2():
    print("Building Page 2: Fund Performance...")
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "xy"}, {"type": "xy"}],
               [{"type": "table", "colspan": 2}, None]],
        row_heights=[0.5, 0.5],
        subplot_titles=("Return vs Risk (Bubble Size = AUM)", "NAV Trend vs Benchmark (Top 5)")
    )

    # Scatter: Return vs Risk
    aum_map = perf.set_index('amfi_code')['aum_crore']
    score_plot = score.copy()
    score_plot['aum'] = score_plot['amfi_code'].map(aum_map).fillna(1000)

    fig.add_trace(go.Scatter(
        x=score_plot['mean_return_ann'], y=score_plot['std_ann'],
        mode='markers',
        marker=dict(size=score_plot['aum']/300, sizemode='area', sizemin=4,
                    color=score_plot['sharpe_ratio'], colorscale='Viridis', showscale=True,
                    colorbar=dict(title="Sharpe", x=0.45, len=0.45, y=0.75)),
        text=score_plot['scheme_name'], hoverinfo="text"
    ), row=1, col=1)

    # NAV vs Benchmark
    top5 = score.head(5)['amfi_code'].tolist()
    start_dt = nav['date'].max() - pd.DateOffset(years=3)
    
    ci = 0
    colors = [BLUE, GREEN, RED, YELLOW, "#9c27b0"]
    for c in top5:
        n = nav[(nav['amfi_code']==c) & (nav['date']>=start_dt)].sort_values('date')
        if len(n) > 0:
            rebased = n['nav'] / n['nav'].iloc[0] * 100
            name = score[score['amfi_code']==c]['scheme_name'].values[0][:20]
            fig.add_trace(go.Scatter(x=n['date'], y=rebased, mode='lines', name=name, line=dict(color=colors[ci])), row=1, col=2)
            ci += 1
            
    nifty = bench[(bench['index_name']=='NIFTY100') & (bench['date']>=start_dt)].sort_values('date')
    if len(nifty) > 0:
        rebased = nifty['close_value'] / nifty['close_value'].iloc[0] * 100
        fig.add_trace(go.Scatter(x=nifty['date'], y=rebased, mode='lines', name='NIFTY 100', line=dict(color='black', dash='dash')), row=1, col=2)

    # Fund Scorecard Table
    sc_disp = score.head(10)[['overall_rank', 'scheme_name', 'composite_score', 'cagr_3yr', 'sharpe_ratio', 'alpha_annual_pct']]
    sc_disp['scheme_name'] = sc_disp['scheme_name'].str[:35]
    sc_disp = sc_disp.round(2)

    fig.add_trace(go.Table(
        header=dict(values=["Rank", "Scheme Name", "Score (0-100)", "3Y CAGR (%)", "Sharpe", "Alpha (%)"],
                    fill_color=BLUE, font=dict(color='white', size=14), align="left"),
        cells=dict(values=[sc_disp[k] for k in sc_disp.columns],
                   fill_color=[PANEL], font=dict(color=TEXT, size=13), align="left", height=30)
    ), row=2, col=1)

    fig.update_layout(title_text="<b>Bluestock Mutual Fund Dashboard | Page 2: Fund Performance</b>", title_font_size=24,
                      plot_bgcolor=PANEL, paper_bgcolor=BGC, font=dict(color=TEXT),
                      margin=dict(t=100, b=50, l=50, r=50))
    fig.update_xaxes(title_text="Annualised Return (%)", row=1, col=1)
    fig.update_yaxes(title_text="Annualised Std Dev (Risk %)", row=1, col=1)
    
    save_fig(fig, "dashboard_page2_performance.png")

# ===========================================================================
# PAGE 3: INVESTOR ANALYTICS
# ===========================================================================
def build_page3():
    print("Building Page 3: Investor Analytics...")
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "xy"}, {"type": "domain"}],
               [{"type": "xy"}, {"type": "xy"}]],
        subplot_titles=("Transaction Amount by State (Top 10)", "Transaction Type Split",
                        "Average SIP Amount by Age Group", "Monthly Transaction Volume")
    )

    # Txn by State
    state_amt = txn.groupby('state')['amount_inr'].sum().nlargest(10).reset_index()
    fig.add_trace(go.Bar(x=state_amt['amount_inr'], y=state_amt['state'], orientation='h', marker_color=BLUE), row=1, col=1)

    # Donut Split
    type_split = txn.groupby('transaction_type')['amount_inr'].sum().reset_index()
    fig.add_trace(go.Pie(labels=type_split['transaction_type'], values=type_split['amount_inr'], hole=0.5, 
                         marker=dict(colors=[BLUE, GREEN, RED])), row=1, col=2)

    # Age vs SIP
    age_sip = txn[txn['transaction_type']=='SIP'].groupby('age_group')['amount_inr'].mean().reset_index()
    fig.add_trace(go.Bar(x=age_sip['age_group'], y=age_sip['amount_inr'], marker_color=GREEN), row=2, col=1)

    # Monthly Txn Vol
    vol = txn.set_index('transaction_date').resample('ME').size().reset_index(name='count')
    fig.add_trace(go.Scatter(x=vol['transaction_date'], y=vol['count'], mode='lines+markers', line=dict(color=RED, width=3)), row=2, col=2)

    fig.update_layout(title_text="<b>Bluestock Mutual Fund Dashboard | Page 3: Investor Analytics</b>", title_font_size=24,
                      plot_bgcolor=PANEL, paper_bgcolor=BGC, font=dict(color=TEXT), showlegend=False,
                      margin=dict(t=100, b=50, l=50, r=50))
    fig.update_yaxes(autorange="reversed", row=1, col=1)
    save_fig(fig, "dashboard_page3_investor.png")

# ===========================================================================
# PAGE 4: SIP & MARKET TRENDS
# ===========================================================================
def build_page4():
    print("Building Page 4: SIP & Market Trends...")
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "xy", "secondary_y": True, "colspan": 2}, None],
               [{"type": "xy"}, {"type": "xy"}]],
        row_heights=[0.5, 0.5],
        subplot_titles=("SIP Inflow vs NIFTY 50", "Category Net Inflows Heatmap (Top 5)", "Top 5 Categories FY25")
    )

    # Dual axis
    nifty = bench[bench['index_name']=='NIFTY50'].set_index('date').resample('ME').last().reset_index()
    s = sip.merge(nifty, left_on='month', right_on='date', how='inner')
    
    fig.add_trace(go.Bar(x=s['month'], y=s['sip_inflow_crore'], name="SIP Inflow", marker_color=BLUE, opacity=0.7), row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=s['month'], y=s['close_value'], name="NIFTY 50", mode="lines", line=dict(color=RED, width=3)), row=1, col=1, secondary_y=True)

    # Heatmap
    c_p = cat.pivot(index='category', columns='month', values='net_inflow_crore')
    c_p = c_p.loc[c_p.sum(axis=1).nlargest(5).index]
    fig.add_trace(go.Heatmap(z=c_p.values, x=c_p.columns, y=c_p.index, colorscale='RdYlGn'), row=2, col=1)

    # Top 5 FY25
    fy25 = cat[cat['month'] >= '2024-04-01'].groupby('category')['net_inflow_crore'].sum().nlargest(5).reset_index()
    fig.add_trace(go.Bar(x=fy25['category'], y=fy25['net_inflow_crore'], marker_color=GREEN), row=2, col=2)

    fig.update_layout(title_text="<b>Bluestock Mutual Fund Dashboard | Page 4: SIP & Market Trends</b>", title_font_size=24,
                      plot_bgcolor=PANEL, paper_bgcolor=BGC, font=dict(color=TEXT), showlegend=False,
                      margin=dict(t=100, b=50, l=50, r=50))
    save_fig(fig, "dashboard_page4_market.png")


def create_pdf():
    print("Compiling Dashboard.pdf...")
    pdf = FPDF(orientation='L', unit='pt', format=[900, 1600])
    
    for i in range(1, 5):
        img_path = os.path.join(DASH_DIR, f"dashboard_page{i}_" + ["industry", "performance", "investor", "market"][i-1] + ".png")
        pdf.add_page()
        pdf.image(img_path, 0, 0, 1600, 900)
        
    pdf_path = os.path.join(DASH_DIR, "Dashboard.pdf")
    pdf.output(pdf_path)
    print(f"Saved: {pdf_path}")

if __name__ == "__main__":
    build_page1()
    build_page2()
    build_page3()
    build_page4()
    create_pdf()
    print("Dashboard deliverables generated successfully!")
