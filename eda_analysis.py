"""
=============================================================================
 Bluestock Fintech — Mutual Fund Capstone Project
 Day 3: Exploratory Data Analysis

 Script: eda_analysis.py
 Purpose: Generate 15+ publication-quality charts as PNGs for the final
          report. Covers NAV trends, AUM growth, SIP flows, demographics,
          geographic distribution, correlations, and sector allocation.
=============================================================================
"""

import os
import sys
import io
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

warnings.filterwarnings("ignore")

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROCESSED_DIR = os.path.join("data", "processed")
CHARTS_DIR = os.path.join("reports", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# Style
sns.set_theme(style="whitegrid", font_scale=1.15)
plt.rcParams.update({
    "figure.figsize": (14, 8),
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "font.family": "sans-serif",
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "axes.labelsize": 13,
})

# Brand-consistent palette
PALETTE = ["#1a73e8", "#34a853", "#ea4335", "#fbbc04", "#9c27b0",
           "#00bcd4", "#ff5722", "#607d8b", "#e91e63", "#8bc34a"]


def sep(char="=", n=80):
    print(char * n)


def header(title):
    sep()
    print(f"  {title}")
    sep()


def save_plotly_png(fig, filename, width=1400, height=750):
    """Save Plotly figure as PNG (needs kaleido) and HTML."""
    html_path = os.path.join(CHARTS_DIR, filename.replace(".png", ".html"))
    fig.write_html(html_path)
    try:
        png_path = os.path.join(CHARTS_DIR, filename)
        fig.write_image(png_path, width=width, height=height, scale=2)
        print(f"  -> Saved: {png_path}")
    except Exception:
        print(f"  -> Saved HTML (install kaleido for PNG): {html_path}")


def save_mpl_png(fig, filename):
    """Save matplotlib figure as PNG."""
    path = os.path.join(CHARTS_DIR, filename)
    fig.savefig(path, bbox_inches="tight", facecolor="white", dpi=150)
    plt.close(fig)
    print(f"  -> Saved: {path}")


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------
def load_data():
    """Load all cleaned datasets."""
    data = {}
    data["fund"]   = pd.read_csv(os.path.join(PROCESSED_DIR, "01_fund_master.csv"))
    data["nav"]    = pd.read_csv(os.path.join(PROCESSED_DIR, "02_nav_history.csv"))
    data["aum"]    = pd.read_csv(os.path.join(PROCESSED_DIR, "03_aum_by_fund_house.csv"))
    data["sip"]    = pd.read_csv(os.path.join(PROCESSED_DIR, "04_monthly_sip_inflows.csv"))
    data["catinf"] = pd.read_csv(os.path.join(PROCESSED_DIR, "05_category_inflows.csv"))
    data["folio"]  = pd.read_csv(os.path.join(PROCESSED_DIR, "06_industry_folio_count.csv"))
    data["perf"]   = pd.read_csv(os.path.join(PROCESSED_DIR, "07_scheme_performance.csv"))
    data["txn"]    = pd.read_csv(os.path.join(PROCESSED_DIR, "08_investor_transactions.csv"))
    data["hold"]   = pd.read_csv(os.path.join(PROCESSED_DIR, "09_portfolio_holdings.csv"))
    data["bench"]  = pd.read_csv(os.path.join(PROCESSED_DIR, "10_benchmark_indices.csv"))

    # Parse dates
    data["nav"]["date"] = pd.to_datetime(data["nav"]["date"])
    data["aum"]["date"] = pd.to_datetime(data["aum"]["date"])
    data["sip"]["month"] = pd.to_datetime(data["sip"]["month"])
    data["catinf"]["month"] = pd.to_datetime(data["catinf"]["month"])
    data["folio"]["month"] = pd.to_datetime(data["folio"]["month"])
    data["txn"]["transaction_date"] = pd.to_datetime(data["txn"]["transaction_date"])
    data["bench"]["date"] = pd.to_datetime(data["bench"]["date"])

    return data


# ============================================================================
# CHART 1: NAV Trend Analysis (Plotly) — 40 schemes 2022-2026
# ============================================================================
def chart_01_nav_trends(data):
    header("Chart 1/15: NAV Trend Analysis (Plotly)")

    df = data["nav"].merge(data["fund"][["amfi_code", "scheme_name", "category", "sub_category"]],
                           on="amfi_code", how="left")

    fig = px.line(
        df, x="date", y="nav", color="scheme_name",
        title="Daily NAV Trends for All 40 Schemes (2022–2026)",
        labels={"nav": "NAV (INR)", "date": "Date", "scheme_name": "Scheme"},
        template="plotly_white",
    )

    # Highlight 2023 Bull Run
    fig.add_vrect(x0="2023-03-01", x1="2023-12-31",
                  fillcolor="green", opacity=0.07, line_width=0,
                  annotation_text="2023 Bull Run", annotation_position="top left",
                  annotation_font_size=12, annotation_font_color="green")

    # Highlight 2024 Correction
    fig.add_vrect(x0="2024-09-01", x1="2025-03-31",
                  fillcolor="red", opacity=0.07, line_width=0,
                  annotation_text="2024-25 Correction", annotation_position="top left",
                  annotation_font_size=12, annotation_font_color="red")

    fig.update_layout(
        height=700, showlegend=False,
        xaxis_title="Date", yaxis_title="NAV (INR)",
        font=dict(size=13),
        title_font_size=18,
    )
    fig.update_layout(hovermode="x unified")

    save_plotly_png(fig, "01_nav_trends.png")


# ============================================================================
# CHART 2: AUM Growth Bar Chart (Seaborn) — by fund house per year
# ============================================================================
def chart_02_aum_growth(data):
    header("Chart 2/15: AUM Growth by Fund House (Seaborn)")

    df = data["aum"].copy()
    df["year"] = df["date"].dt.year

    # Pivot for grouped bar
    pivot = df.groupby(["fund_house", "year"])["aum_lakh_crore"].mean().reset_index()
    pivot["fund_house_short"] = pivot["fund_house"].str.replace(" Mutual Fund", "").str.replace(" MF", "")

    fig, ax = plt.subplots(figsize=(16, 9))
    bars = sns.barplot(data=pivot, x="fund_house_short", y="aum_lakh_crore",
                       hue="year", palette="viridis", ax=ax)

    # Highlight SBI
    for patch in ax.patches:
        if patch.get_height() > 10:
            patch.set_edgecolor("#ea4335")
            patch.set_linewidth(2.5)

    ax.set_title("AUM Growth by Fund House (2022–2025)\nSBI Dominates at ~12.5 Lakh Crore",
                 fontsize=17, fontweight="bold", pad=15)
    ax.set_xlabel("Fund House", fontsize=13)
    ax.set_ylabel("AUM (Lakh Crore INR)", fontsize=13)
    plt.xticks(rotation=30, ha="right", fontsize=11)
    ax.legend(title="Year", fontsize=11, title_fontsize=12)

    # Add value labels on top bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", fontsize=8, padding=2)

    plt.tight_layout()
    save_mpl_png(fig, "02_aum_growth.png")


# ============================================================================
# CHART 3: SIP Inflow Time Series (Plotly) — annotate peak
# ============================================================================
def chart_03_sip_inflow(data):
    header("Chart 3/15: SIP Inflow Time Series (Plotly)")

    df = data["sip"].copy().sort_values("month")

    # Find the all-time high
    peak_idx = df["sip_inflow_crore"].idxmax()
    peak_row = df.loc[peak_idx]
    peak_val = peak_row["sip_inflow_crore"]
    peak_date = peak_row["month"]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar for SIP inflow
    fig.add_trace(
        go.Bar(x=df["month"], y=df["sip_inflow_crore"], name="SIP Inflow (Cr)",
               marker_color="#1a73e8", opacity=0.8),
        secondary_y=False,
    )

    # Line for active accounts
    fig.add_trace(
        go.Scatter(x=df["month"], y=df["active_sip_accounts_crore"],
                   name="Active SIP Accounts (Cr)", mode="lines+markers",
                   line=dict(color="#ea4335", width=3), marker=dict(size=6)),
        secondary_y=True,
    )

    # Annotate the all-time high
    fig.add_annotation(
        x=peak_date, y=peak_val,
        text=f"All-Time High<br>Rs {peak_val:,} Cr",
        showarrow=True, arrowhead=2, arrowsize=1.5,
        ax=0, ay=-60,
        font=dict(size=14, color="#ea4335"),
        bgcolor="white", bordercolor="#ea4335", borderwidth=2,
    )

    fig.update_layout(
        title=f"Monthly SIP Inflow Trend (Jan 2022 – Dec 2025)<br>"
              f"<sub>All-time high of Rs {peak_val:,} Cr in {peak_date.strftime('%b %Y')}</sub>",
        template="plotly_white",
        height=650,
        xaxis_title="Month",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        title_font_size=17,
    )
    fig.update_yaxes(title_text="SIP Inflow (Crore INR)", secondary_y=False)
    fig.update_yaxes(title_text="Active SIP Accounts (Crore)", secondary_y=True)

    save_plotly_png(fig, "03_sip_inflow.png")


# ============================================================================
# CHART 4: Category Inflow Heatmap (Seaborn)
# ============================================================================
def chart_04_category_heatmap(data):
    header("Chart 4/15: Category Inflow Heatmap (Seaborn)")

    df = data["catinf"].copy()
    df["month_label"] = df["month"].dt.strftime("%Y-%m")

    # Pivot
    pivot = df.pivot_table(index="category", columns="month_label",
                           values="net_inflow_crore", aggfunc="sum")
    pivot = pivot.fillna(0)

    fig, ax = plt.subplots(figsize=(18, 10))
    sns.heatmap(pivot, cmap="RdYlGn", center=0, annot=True, fmt=".0f",
                linewidths=0.5, linecolor="white",
                cbar_kws={"label": "Net Inflow (Crore INR)", "shrink": 0.8},
                ax=ax, annot_kws={"size": 8})

    ax.set_title("Category-wise Monthly Net Inflows Heatmap\nGreen = Inflow | Red = Outflow",
                 fontsize=17, fontweight="bold", pad=15)
    ax.set_xlabel("Month", fontsize=13)
    ax.set_ylabel("Fund Category", fontsize=13)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    save_mpl_png(fig, "04_category_heatmap.png")


# ============================================================================
# CHART 5: Age Group Pie Chart (Matplotlib)
# ============================================================================
def chart_05_age_pie(data):
    header("Chart 5/15: Age Group Distribution Pie Chart")

    df = data["txn"].copy()
    age_dist = df["age_group"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 10))
    colors = sns.color_palette("husl", n_colors=len(age_dist))
    wedges, texts, autotexts = ax.pie(
        age_dist.values, labels=age_dist.index,
        autopct="%1.1f%%", startangle=90,
        colors=colors, pctdistance=0.82,
        wedgeprops=dict(width=0.5, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=13),
    )
    for at in autotexts:
        at.set_fontsize(12)
        at.set_fontweight("bold")

    ax.set_title("Investor Age Group Distribution\nWho's Investing in Mutual Funds?",
                 fontsize=17, fontweight="bold", pad=20)

    centre = plt.Circle((0, 0), 0.50, fc="white")
    ax.add_artist(centre)
    ax.text(0, 0, f"{len(df):,}\nTotal Txns", ha="center", va="center",
            fontsize=16, fontweight="bold", color="#202124")

    plt.tight_layout()
    save_mpl_png(fig, "05_age_pie.png")


# ============================================================================
# CHART 6: SIP Amount Box Plot by Age Group (Seaborn)
# ============================================================================
def chart_06_sip_boxplot(data):
    header("Chart 6/15: SIP Amount Box Plot by Age Group")

    df = data["txn"][data["txn"]["transaction_type"] == "SIP"].copy()

    fig, ax = plt.subplots(figsize=(14, 8))
    sns.boxplot(data=df, x="age_group", y="amount_inr",
                palette="husl", order=sorted(df["age_group"].unique()),
                fliersize=2, linewidth=1.5, ax=ax)

    ax.set_title("SIP Investment Amount Distribution by Age Group",
                 fontsize=17, fontweight="bold", pad=15)
    ax.set_xlabel("Age Group", fontsize=13)
    ax.set_ylabel("SIP Amount (INR)", fontsize=13)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rs {x:,.0f}"))

    # Add median labels
    medians = df.groupby("age_group")["amount_inr"].median().sort_index()
    for i, (grp, med) in enumerate(medians.items()):
        ax.text(i, med + 200, f"Rs {med:,.0f}", ha="center", fontsize=10,
                fontweight="bold", color="#202124")

    plt.tight_layout()
    save_mpl_png(fig, "06_sip_boxplot.png")


# ============================================================================
# CHART 7: Gender Split (Seaborn)
# ============================================================================
def chart_07_gender_split(data):
    header("Chart 7/15: Gender Split by Transaction Type")

    df = data["txn"].copy()
    gender_txn = df.groupby(["gender", "transaction_type"]).agg(
        count=("amount_inr", "count"),
        total_amount=("amount_inr", "sum"),
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Count
    sns.barplot(data=gender_txn, x="transaction_type", y="count",
                hue="gender", palette=["#1a73e8", "#ea4335"], ax=axes[0])
    axes[0].set_title("Transaction Count by Gender", fontsize=15, fontweight="bold")
    axes[0].set_xlabel("Transaction Type", fontsize=12)
    axes[0].set_ylabel("Count", fontsize=12)
    for container in axes[0].containers:
        axes[0].bar_label(container, fmt="{:,.0f}", fontsize=9, padding=3)

    # Total Amount
    gender_txn["total_cr"] = gender_txn["total_amount"] / 1e7
    sns.barplot(data=gender_txn, x="transaction_type", y="total_cr",
                hue="gender", palette=["#1a73e8", "#ea4335"], ax=axes[1])
    axes[1].set_title("Total Amount by Gender", fontsize=15, fontweight="bold")
    axes[1].set_xlabel("Transaction Type", fontsize=12)
    axes[1].set_ylabel("Total Amount (Crore INR)", fontsize=12)
    for container in axes[1].containers:
        axes[1].bar_label(container, fmt="{:.0f} Cr", fontsize=9, padding=3)

    plt.suptitle("Gender-wise Investment Analysis", fontsize=18, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_mpl_png(fig, "07_gender_split.png")


# ============================================================================
# CHART 8: Geographic Distribution — State Bar (Seaborn)
# ============================================================================
def chart_08_geographic_state(data):
    header("Chart 8/15: Geographic Distribution by State")

    df = data["txn"][data["txn"]["transaction_type"] == "SIP"].copy()
    state_agg = df.groupby("state")["amount_inr"].sum().sort_values(ascending=True).tail(15)
    state_agg_cr = state_agg / 1e7

    fig, ax = plt.subplots(figsize=(14, 9))
    bars = ax.barh(state_agg_cr.index, state_agg_cr.values, color=PALETTE[0], edgecolor="white")

    # Highlight top 3
    for bar in bars[-3:]:
        bar.set_color("#ea4335")

    ax.set_title("Top 15 States by Total SIP Investment\nTop 3 States Highlighted in Red",
                 fontsize=17, fontweight="bold", pad=15)
    ax.set_xlabel("Total SIP Amount (Crore INR)", fontsize=13)
    ax.set_ylabel("State", fontsize=13)

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.2, bar.get_y() + bar.get_height() / 2,
                f"Rs {width:.0f} Cr", va="center", fontsize=10, fontweight="bold")

    plt.tight_layout()
    save_mpl_png(fig, "08_geographic_state.png")


# ============================================================================
# CHART 9: T30 vs B30 City Tier Pie (Matplotlib)
# ============================================================================
def chart_09_city_tier(data):
    header("Chart 9/15: T30 vs B30 City Tier Split")

    df = data["txn"].copy()
    tier_agg = df.groupby("city_tier").agg(
        count=("amount_inr", "count"),
        total=("amount_inr", "sum")
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    for i, (metric, title) in enumerate([("count", "Transaction Count"), ("total", "Total Amount")]):
        vals = tier_agg[metric].values
        labels = tier_agg["city_tier"].values
        colors = ["#1a73e8", "#fbbc04"]
        wedges, texts, autotexts = axes[i].pie(
            vals, labels=labels, autopct="%1.1f%%",
            colors=colors, startangle=90,
            wedgeprops=dict(edgecolor="white", linewidth=2),
            textprops=dict(fontsize=14),
        )
        for at in autotexts:
            at.set_fontsize(14)
            at.set_fontweight("bold")
        axes[i].set_title(f"by {title}", fontsize=14, fontweight="bold")

    plt.suptitle("T30 (Metro) vs B30 (Non-Metro) City Tier Distribution",
                 fontsize=17, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_mpl_png(fig, "09_city_tier.png")


# ============================================================================
# CHART 10: Folio Count Growth (Plotly) — with milestones
# ============================================================================
def chart_10_folio_growth(data):
    header("Chart 10/15: Folio Count Growth (Plotly)")

    df = data["folio"].copy().sort_values("month")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["month"], y=df["total_folios_crore"],
        mode="lines+markers",
        name="Total Folios",
        line=dict(color="#1a73e8", width=3),
        marker=dict(size=10, line=dict(width=2, color="white")),
        fill="tozeroy", fillcolor="rgba(26,115,232,0.12)",
    ))

    # Milestones
    first_val = df.iloc[0]["total_folios_crore"]
    last_val = df.iloc[-1]["total_folios_crore"]

    milestones = [
        (df.iloc[0]["month"], first_val, f"Start: {first_val} Cr"),
        (df.iloc[-1]["month"], last_val, f"Latest: {last_val} Cr"),
    ]

    # Find when 15 Cr, 20 Cr crossed
    for target in [15, 20, 25]:
        crossed = df[df["total_folios_crore"] >= target]
        if len(crossed) > 0:
            row = crossed.iloc[0]
            milestones.append((row["month"], row["total_folios_crore"],
                             f"Crossed {target} Cr"))

    for date, val, text in milestones:
        fig.add_annotation(
            x=date, y=val, text=text,
            showarrow=True, arrowhead=2,
            ax=0, ay=-40 if val > first_val + 2 else 40,
            font=dict(size=12, color="#202124"),
            bgcolor="white", bordercolor="#1a73e8", borderwidth=1.5,
        )

    growth_pct = (last_val - first_val) / first_val * 100
    fig.update_layout(
        title=f"MF Folio Count Growth: {first_val} Cr to {last_val} Cr "
              f"(+{growth_pct:.0f}%)",
        template="plotly_white",
        height=600,
        xaxis_title="Date",
        yaxis_title="Total Folios (Crore)",
        title_font_size=17,
        showlegend=False,
    )

    save_plotly_png(fig, "10_folio_growth.png")


# ============================================================================
# CHART 11: NAV Return Correlation Matrix (Seaborn)
# ============================================================================
def chart_11_correlation(data):
    header("Chart 11/15: NAV Return Correlation Heatmap")

    # Select 10 representative funds (one per fund house, mix of categories)
    selected_codes = [119551, 125497, 120503, 118632, 119092,
                      120841, 101206, 102885, 148567, 149322]

    df_nav = data["nav"][data["nav"]["amfi_code"].isin(selected_codes)].copy()
    df_fund = data["fund"][["amfi_code", "scheme_name"]].copy()

    # Pivot to get NAV per scheme per date
    pivot = df_nav.pivot_table(index="date", columns="amfi_code", values="nav")

    # Compute daily returns
    returns = pivot.pct_change().dropna()

    # Map codes to short names
    code_to_name = {}
    for code in selected_codes:
        name = df_fund[df_fund["amfi_code"] == code]["scheme_name"].values
        if len(name) > 0:
            short = name[0].split(" - ")[0][:25]
            code_to_name[code] = short
        else:
            code_to_name[code] = str(code)

    returns.columns = [code_to_name.get(c, str(c)) for c in returns.columns]

    # Correlation matrix
    corr = returns.corr()

    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
                cmap="RdYlBu_r", center=0.5, vmin=0, vmax=1,
                linewidths=1, linecolor="white",
                cbar_kws={"label": "Correlation", "shrink": 0.8},
                ax=ax, annot_kws={"size": 11, "fontweight": "bold"})

    ax.set_title("Pairwise Correlation of Daily NAV Returns\n10 Selected Funds",
                 fontsize=17, fontweight="bold", pad=15)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    save_mpl_png(fig, "11_correlation_matrix.png")


# ============================================================================
# CHART 12: Sector Allocation Donut (Matplotlib)
# ============================================================================
def chart_12_sector_donut(data):
    header("Chart 12/15: Sector Allocation Donut Chart")

    df = data["hold"].copy()

    # Merge with fund master to filter equity funds
    df = df.merge(data["fund"][["amfi_code", "category"]], on="amfi_code", how="left")
    df_eq = df[df["category"] == "Equity"]

    # Aggregate sector weights
    sector_agg = df_eq.groupby("sector")["weight_pct"].sum().sort_values(ascending=False)

    # Keep top 10 sectors, group rest as "Others"
    top10 = sector_agg.head(10)
    others = sector_agg.iloc[10:].sum()
    if others > 0:
        top10 = pd.concat([top10, pd.Series({"Others": others})])

    fig, ax = plt.subplots(figsize=(11, 11))
    colors = sns.color_palette("husl", n_colors=len(top10))

    wedges, texts, autotexts = ax.pie(
        top10.values, labels=top10.index,
        autopct="%1.1f%%", startangle=140,
        colors=colors, pctdistance=0.82,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=11),
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")

    centre = plt.Circle((0, 0), 0.55, fc="white")
    ax.add_artist(centre)
    ax.text(0, 0, "Sector\nAllocation", ha="center", va="center",
            fontsize=16, fontweight="bold", color="#202124")

    ax.set_title("Aggregate Sector Allocation Across Equity Funds\nFrom Portfolio Holdings",
                 fontsize=17, fontweight="bold", pad=20)
    plt.tight_layout()
    save_mpl_png(fig, "12_sector_donut.png")


# ============================================================================
# CHART 13: Expense Ratio vs 3Y Return Scatter (Seaborn)
# ============================================================================
def chart_13_expense_vs_return(data):
    header("Chart 13/15: Expense Ratio vs 3-Year Return Scatter")

    df = data["perf"].copy()
    df["category_short"] = df["category"]

    fig, ax = plt.subplots(figsize=(14, 9))
    scatter = sns.scatterplot(
        data=df, x="expense_ratio_pct", y="return_3yr_pct",
        hue="category_short", size="aum_crore",
        sizes=(80, 600), alpha=0.75, palette="husl", ax=ax,
        edgecolor="white", linewidth=1.5,
    )

    # Add scheme labels for outliers
    for _, row in df.iterrows():
        if row["return_3yr_pct"] > 20 or row["expense_ratio_pct"] < 0.6:
            short_name = row["scheme_name"].split(" - ")[0][:20]
            ax.annotate(short_name, (row["expense_ratio_pct"], row["return_3yr_pct"]),
                       fontsize=8, alpha=0.8, ha="left",
                       xytext=(5, 5), textcoords="offset points")

    ax.set_title("Expense Ratio vs 3-Year Return\nBubble Size = AUM",
                 fontsize=17, fontweight="bold", pad=15)
    ax.set_xlabel("Expense Ratio (%)", fontsize=13)
    ax.set_ylabel("3-Year CAGR Return (%)", fontsize=13)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)

    # Add quadrant lines
    ax.axhline(y=df["return_3yr_pct"].median(), color="gray", linestyle="--", alpha=0.4)
    ax.axvline(x=df["expense_ratio_pct"].median(), color="gray", linestyle="--", alpha=0.4)

    plt.tight_layout()
    save_mpl_png(fig, "13_expense_vs_return.png")


# ============================================================================
# CHART 14: Monthly Transaction Volume Stacked Area (Matplotlib)
# ============================================================================
def chart_14_txn_volume(data):
    header("Chart 14/15: Monthly Transaction Volume by Type")

    df = data["txn"].copy()
    df["month"] = df["transaction_date"].dt.to_period("M").dt.to_timestamp()

    monthly = df.groupby(["month", "transaction_type"])["amount_inr"].count().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(15, 8))
    monthly.plot.area(stacked=True, alpha=0.75, ax=ax,
                      color=["#1a73e8", "#34a853", "#ea4335"])

    ax.set_title("Monthly Transaction Volume by Type (Stacked Area)",
                 fontsize=17, fontweight="bold", pad=15)
    ax.set_xlabel("Month", fontsize=13)
    ax.set_ylabel("Number of Transactions", fontsize=13)
    ax.legend(title="Transaction Type", fontsize=11, title_fontsize=12,
              loc="upper left")

    plt.tight_layout()
    save_mpl_png(fig, "14_txn_volume.png")


# ============================================================================
# CHART 15: Morningstar Rating Distribution (Seaborn)
# ============================================================================
def chart_15_morningstar(data):
    header("Chart 15/15: Morningstar Rating Distribution")

    df = data["perf"].copy()

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Count distribution
    rating_counts = df["morningstar_rating"].value_counts().sort_index()
    colors_stars = ["#ea4335", "#fbbc04", "#ff9800", "#34a853", "#1a73e8"]
    bars = axes[0].bar(rating_counts.index, rating_counts.values, color=colors_stars,
                       edgecolor="white", linewidth=2)
    axes[0].set_title("Fund Count by Morningstar Rating", fontsize=15, fontweight="bold")
    axes[0].set_xlabel("Morningstar Rating (Stars)", fontsize=12)
    axes[0].set_ylabel("Number of Funds", fontsize=12)
    axes[0].set_xticks(range(1, 6))
    axes[0].set_xticklabels(["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"])
    for bar in bars:
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                    f"{int(bar.get_height())}", ha="center", fontsize=13, fontweight="bold")

    # Avg return by rating
    avg_ret = df.groupby("morningstar_rating")["return_3yr_pct"].mean()
    axes[1].bar(avg_ret.index, avg_ret.values, color=colors_stars,
                edgecolor="white", linewidth=2)
    axes[1].set_title("Avg 3-Year Return by Morningstar Rating", fontsize=15, fontweight="bold")
    axes[1].set_xlabel("Morningstar Rating (Stars)", fontsize=12)
    axes[1].set_ylabel("Avg 3Y Return (%)", fontsize=12)
    axes[1].set_xticks(range(1, 6))
    axes[1].set_xticklabels(["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"])
    for i, v in enumerate(avg_ret.values):
        axes[1].text(avg_ret.index[i], v + 0.3, f"{v:.1f}%", ha="center",
                    fontsize=12, fontweight="bold")

    plt.suptitle("Morningstar Rating Analysis", fontsize=18, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_mpl_png(fig, "15_morningstar.png")


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n")
    header("BLUESTOCK FINTECH - DAY 3: EXPLORATORY DATA ANALYSIS")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Charts output: {os.path.abspath(CHARTS_DIR)}")
    sep()

    data = load_data()
    print(f"\n  Loaded {len(data)} datasets successfully.\n")

    chart_01_nav_trends(data)
    chart_02_aum_growth(data)
    chart_03_sip_inflow(data)
    chart_04_category_heatmap(data)
    chart_05_age_pie(data)
    chart_06_sip_boxplot(data)
    chart_07_gender_split(data)
    chart_08_geographic_state(data)
    chart_09_city_tier(data)
    chart_10_folio_growth(data)
    chart_11_correlation(data)
    chart_12_sector_donut(data)
    chart_13_expense_vs_return(data)
    chart_14_txn_volume(data)
    chart_15_morningstar(data)

    # Summary
    charts = [f for f in os.listdir(CHARTS_DIR) if f.endswith((".png", ".html"))]
    header("EDA ANALYSIS COMPLETE")
    print(f"\n  Total charts generated: {len(charts)}")
    print(f"  PNGs: {len([c for c in charts if c.endswith('.png')])}")
    print(f"  HTMLs: {len([c for c in charts if c.endswith('.html')])}")
    print(f"  Output directory: {os.path.abspath(CHARTS_DIR)}")
    print(f"  Completed at {datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == "__main__":
    main()
