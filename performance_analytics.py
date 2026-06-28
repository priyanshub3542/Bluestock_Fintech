"""
=============================================================================
 Bluestock Fintech — Mutual Fund Capstone Project
 Day 4: Performance Analytics

 Script: performance_analytics.py
 Purpose: Compute daily returns, CAGR, Sharpe, Sortino, Alpha, Beta,
          Max Drawdown, Fund Scorecard, and Benchmark Comparison.
 Outputs: fund_scorecard.csv, alpha_beta.csv, benchmark charts
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
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from datetime import datetime

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROCESSED_DIR = os.path.join("data", "processed")
CHARTS_DIR = os.path.join("reports", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

RF_ANNUAL = 0.065          # Risk-free rate (6.5% RBI repo rate proxy)
RF_DAILY = RF_ANNUAL / 252  # Daily risk-free rate
TRADING_DAYS = 252

sns.set_theme(style="whitegrid", font_scale=1.15)
plt.rcParams.update({
    "figure.figsize": (14, 8), "figure.dpi": 150,
    "savefig.dpi": 150, "savefig.bbox": "tight", "savefig.facecolor": "white",
    "axes.titlesize": 16, "axes.titleweight": "bold", "axes.labelsize": 13,
})
PALETTE = ["#1a73e8", "#34a853", "#ea4335", "#fbbc04", "#9c27b0",
           "#00bcd4", "#ff5722", "#607d8b", "#e91e63", "#8bc34a"]


def sep(char="=", n=80):
    print(char * n)

def header(title):
    sep()
    print(f"  {title}")
    sep()


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------
def load_data():
    """Load NAV, fund master, performance, and benchmark data."""
    nav = pd.read_csv(os.path.join(PROCESSED_DIR, "02_nav_history.csv"),
                      parse_dates=["date"])
    fund = pd.read_csv(os.path.join(PROCESSED_DIR, "01_fund_master.csv"))
    perf = pd.read_csv(os.path.join(PROCESSED_DIR, "07_scheme_performance.csv"))
    bench = pd.read_csv(os.path.join(PROCESSED_DIR, "10_benchmark_indices.csv"),
                        parse_dates=["date"])
    return nav, fund, perf, bench


# ============================================================================
# 1. DAILY RETURNS
# ============================================================================
def compute_daily_returns(nav):
    """Compute daily returns: r_t = NAV_t / NAV_{t-1} - 1"""
    header("1. Computing Daily Returns")

    nav_sorted = nav.sort_values(["amfi_code", "date"]).copy()
    nav_sorted["daily_return"] = nav_sorted.groupby("amfi_code")["nav"].pct_change()

    # Validate distribution
    returns_all = nav_sorted["daily_return"].dropna()
    print(f"  Total return observations: {len(returns_all):,}")
    print(f"  Mean daily return:  {returns_all.mean():.6f} ({returns_all.mean()*252:.2f}% annualised)")
    print(f"  Std daily return:   {returns_all.std():.6f} ({returns_all.std()*np.sqrt(252):.2f}% annualised)")
    print(f"  Min daily return:   {returns_all.min():.4f} ({returns_all.min()*100:.2f}%)")
    print(f"  Max daily return:   {returns_all.max():.4f} ({returns_all.max()*100:.2f}%)")
    print(f"  Skewness:           {returns_all.skew():.4f}")
    print(f"  Kurtosis:           {returns_all.kurtosis():.4f}")

    # Distribution chart
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    axes[0].hist(returns_all, bins=100, color="#1a73e8", edgecolor="white",
                 alpha=0.8, density=True)
    axes[0].axvline(returns_all.mean(), color="#ea4335", linewidth=2, label=f"Mean: {returns_all.mean():.5f}")
    axes[0].set_title("Distribution of Daily Returns (All Funds)", fontsize=15, fontweight="bold")
    axes[0].set_xlabel("Daily Return")
    axes[0].set_ylabel("Density")
    axes[0].legend(fontsize=11)

    # QQ plot
    stats.probplot(returns_all.sample(min(5000, len(returns_all)), random_state=42),
                   dist="norm", plot=axes[1])
    axes[1].set_title("QQ Plot — Daily Returns vs Normal", fontsize=15, fontweight="bold")
    axes[1].get_lines()[0].set_color("#1a73e8")
    axes[1].get_lines()[1].set_color("#ea4335")

    plt.suptitle("Daily Return Distribution Validation", fontsize=17, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "16_return_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  -> Saved: {CHARTS_DIR}/16_return_distribution.png")

    return nav_sorted


# ============================================================================
# 2. CAGR (1yr, 3yr, 5yr)
# ============================================================================
def compute_cagr(nav_with_returns, fund):
    """Compute CAGR = (NAV_end / NAV_start) ^ (1/n) - 1"""
    header("2. Computing CAGR (1yr, 3yr, 5yr)")

    latest_date = nav_with_returns["date"].max()
    results = []

    for code in nav_with_returns["amfi_code"].unique():
        scheme_nav = nav_with_returns[nav_with_returns["amfi_code"] == code].sort_values("date")
        nav_end = scheme_nav.iloc[-1]["nav"]
        end_date = scheme_nav.iloc[-1]["date"]
        row = {"amfi_code": code, "nav_end": nav_end, "end_date": end_date}

        for years, label in [(1, "cagr_1yr"), (3, "cagr_3yr"), (5, "cagr_5yr")]:
            target_date = end_date - pd.DateOffset(years=years)
            past = scheme_nav[scheme_nav["date"] <= target_date]
            if len(past) > 0:
                nav_start = past.iloc[-1]["nav"]
                actual_days = (end_date - past.iloc[-1]["date"]).days
                actual_years = actual_days / 365.25
                if actual_years > 0 and nav_start > 0:
                    cagr = (nav_end / nav_start) ** (1 / actual_years) - 1
                    row[label] = round(cagr * 100, 2)
                else:
                    row[label] = None
            else:
                row[label] = None

        results.append(row)

    cagr_df = pd.DataFrame(results)
    cagr_df = cagr_df.merge(fund[["amfi_code", "scheme_name", "fund_house", "sub_category", "plan"]],
                            on="amfi_code", how="left")

    # Reorder columns
    cols = ["amfi_code", "scheme_name", "fund_house", "sub_category", "plan",
            "cagr_1yr", "cagr_3yr", "cagr_5yr"]
    cagr_df = cagr_df[[c for c in cols if c in cagr_df.columns]]

    print(f"  CAGR computed for {len(cagr_df)} schemes")
    print(f"\n  Top 5 by 3-Year CAGR:")
    top5 = cagr_df.nlargest(5, "cagr_3yr")[["scheme_name", "cagr_1yr", "cagr_3yr", "cagr_5yr"]]
    for _, r in top5.iterrows():
        print(f"    {r['scheme_name'][:40]:<42} 1Y:{r['cagr_1yr']:>6}%  3Y:{r['cagr_3yr']:>6}%")

    return cagr_df


# ============================================================================
# 3. SHARPE RATIO
# ============================================================================
def compute_sharpe(nav_with_returns, fund):
    """Sharpe = (Rp - Rf) / Std(Rp) * sqrt(252)"""
    header("3. Computing Sharpe Ratio")

    results = []
    for code in nav_with_returns["amfi_code"].unique():
        rets = nav_with_returns[nav_with_returns["amfi_code"] == code]["daily_return"].dropna()
        if len(rets) < 30:
            continue
        excess = rets - RF_DAILY
        sharpe = (excess.mean() / excess.std()) * np.sqrt(TRADING_DAYS)
        results.append({"amfi_code": code, "sharpe_ratio": round(sharpe, 4),
                        "mean_return_ann": round(rets.mean() * 252 * 100, 2),
                        "std_ann": round(rets.std() * np.sqrt(252) * 100, 2)})

    sharpe_df = pd.DataFrame(results)
    sharpe_df = sharpe_df.merge(fund[["amfi_code", "scheme_name", "sub_category"]],
                                on="amfi_code", how="left")
    sharpe_df["sharpe_rank"] = sharpe_df["sharpe_ratio"].rank(ascending=False).astype(int)
    sharpe_df = sharpe_df.sort_values("sharpe_rank")

    print(f"  Sharpe computed for {len(sharpe_df)} schemes (Rf = {RF_ANNUAL*100}%)")
    print(f"\n  Top 5 by Sharpe Ratio:")
    for _, r in sharpe_df.head(5).iterrows():
        print(f"    #{r['sharpe_rank']:<3} {r['scheme_name'][:40]:<42} Sharpe: {r['sharpe_ratio']:.4f}")

    return sharpe_df


# ============================================================================
# 4. SORTINO RATIO
# ============================================================================
def compute_sortino(nav_with_returns, fund):
    """Sortino = (Rp - Rf) / Downside_Std(Rp) * sqrt(252)"""
    header("4. Computing Sortino Ratio")

    results = []
    for code in nav_with_returns["amfi_code"].unique():
        rets = nav_with_returns[nav_with_returns["amfi_code"] == code]["daily_return"].dropna()
        if len(rets) < 30:
            continue
        excess = rets - RF_DAILY
        downside = rets[rets < 0]
        downside_std = downside.std()
        if downside_std > 0:
            sortino = (excess.mean() / downside_std) * np.sqrt(TRADING_DAYS)
        else:
            sortino = np.nan
        results.append({"amfi_code": code, "sortino_ratio": round(sortino, 4),
                        "downside_std_ann": round(downside_std * np.sqrt(252) * 100, 2),
                        "pct_negative_days": round(len(downside) / len(rets) * 100, 1)})

    sortino_df = pd.DataFrame(results)
    sortino_df = sortino_df.merge(fund[["amfi_code", "scheme_name"]],
                                  on="amfi_code", how="left")
    sortino_df["sortino_rank"] = sortino_df["sortino_ratio"].rank(ascending=False).astype(int)

    print(f"  Sortino computed for {len(sortino_df)} schemes")
    print(f"\n  Top 5 by Sortino Ratio:")
    for _, r in sortino_df.sort_values("sortino_rank").head(5).iterrows():
        print(f"    #{r['sortino_rank']:<3} {r['scheme_name'][:40]:<42} Sortino: {r['sortino_ratio']:.4f}")

    return sortino_df


# ============================================================================
# 5. ALPHA & BETA (OLS regression vs Nifty 100)
# ============================================================================
def compute_alpha_beta(nav_with_returns, fund, bench):
    """OLS: fund_return = alpha + beta * benchmark_return + epsilon"""
    header("5. Computing Alpha & Beta (vs NIFTY 100)")

    # Prepare benchmark returns (NIFTY100)
    nifty100 = bench[bench["index_name"] == "NIFTY100"].sort_values("date").copy()
    nifty100["bench_return"] = nifty100["close_value"].pct_change()
    nifty100 = nifty100[["date", "bench_return"]].dropna()

    results = []
    for code in nav_with_returns["amfi_code"].unique():
        fund_rets = nav_with_returns[nav_with_returns["amfi_code"] == code][["date", "daily_return"]].dropna()

        # Merge on date
        merged = fund_rets.merge(nifty100, on="date", how="inner")
        if len(merged) < 60:
            continue

        # OLS regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            merged["bench_return"], merged["daily_return"]
        )

        beta = round(slope, 4)
        alpha_daily = intercept
        alpha_annual = round(alpha_daily * TRADING_DAYS * 100, 2)  # Annualised %
        r_squared = round(r_value ** 2, 4)

        results.append({
            "amfi_code": code,
            "alpha_annual_pct": alpha_annual,
            "beta": beta,
            "r_squared": r_squared,
            "p_value": round(p_value, 6),
            "observations": len(merged),
        })

    ab_df = pd.DataFrame(results)
    ab_df = ab_df.merge(fund[["amfi_code", "scheme_name", "fund_house", "sub_category", "plan",
                              "expense_ratio_pct"]],
                        on="amfi_code", how="left")

    cols = ["amfi_code", "scheme_name", "fund_house", "sub_category", "plan",
            "alpha_annual_pct", "beta", "r_squared", "p_value", "expense_ratio_pct", "observations"]
    ab_df = ab_df[[c for c in cols if c in ab_df.columns]]
    ab_df = ab_df.sort_values("alpha_annual_pct", ascending=False)

    # Save alpha_beta.csv
    ab_df.to_csv("alpha_beta.csv", index=False)
    print(f"  Alpha/Beta computed for {len(ab_df)} schemes")
    print(f"  -> Saved: alpha_beta.csv")
    print(f"\n  Top 5 by Alpha:")
    for _, r in ab_df.head(5).iterrows():
        print(f"    {r['scheme_name'][:40]:<42} Alpha: {r['alpha_annual_pct']:>6}%  Beta: {r['beta']:.3f}  R2: {r['r_squared']:.3f}")

    # Alpha-Beta scatter chart
    fig, ax = plt.subplots(figsize=(14, 9))
    scatter = ax.scatter(ab_df["beta"], ab_df["alpha_annual_pct"],
                         c=ab_df["r_squared"], s=120, cmap="RdYlGn",
                         edgecolors="white", linewidth=1.5, alpha=0.85)
    plt.colorbar(scatter, ax=ax, label="R-squared", shrink=0.8)

    # Label notable funds
    for _, r in ab_df.head(5).iterrows():
        ax.annotate(r["scheme_name"].split(" - ")[0][:20],
                    (r["beta"], r["alpha_annual_pct"]),
                    fontsize=8, alpha=0.9, xytext=(5, 5), textcoords="offset points")
    for _, r in ab_df.tail(3).iterrows():
        ax.annotate(r["scheme_name"].split(" - ")[0][:20],
                    (r["beta"], r["alpha_annual_pct"]),
                    fontsize=8, alpha=0.9, xytext=(5, -10), textcoords="offset points")

    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5, linewidth=1)
    ax.axvline(x=1, color="gray", linestyle="--", alpha=0.5, linewidth=1)
    ax.set_title("Alpha vs Beta — All 40 Funds (Benchmark: NIFTY 100)\nColor = R-squared",
                 fontsize=17, fontweight="bold", pad=15)
    ax.set_xlabel("Beta (Systematic Risk)", fontsize=13)
    ax.set_ylabel("Annual Alpha (%)", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "17_alpha_beta_scatter.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> Saved: {CHARTS_DIR}/17_alpha_beta_scatter.png")

    return ab_df


# ============================================================================
# 6. MAXIMUM DRAWDOWN
# ============================================================================
def compute_max_drawdown(nav_with_returns, fund):
    """Max Drawdown = min(NAV / running_max - 1)"""
    header("6. Computing Maximum Drawdown")

    results = []
    for code in nav_with_returns["amfi_code"].unique():
        scheme = nav_with_returns[nav_with_returns["amfi_code"] == code].sort_values("date").copy()
        scheme["running_max"] = scheme["nav"].cummax()
        scheme["drawdown"] = scheme["nav"] / scheme["running_max"] - 1

        max_dd = scheme["drawdown"].min()
        max_dd_date = scheme.loc[scheme["drawdown"].idxmin(), "date"]

        # Find peak and trough dates for worst drawdown
        peak_date = scheme.loc[scheme.loc[:scheme["drawdown"].idxmin(), "nav"].idxmax(), "date"]
        trough_date = max_dd_date

        # Recovery date (if any)
        peak_nav = scheme[scheme["date"] == peak_date]["nav"].values[0]
        recovery = scheme[(scheme["date"] > trough_date) & (scheme["nav"] >= peak_nav)]
        recovery_date = recovery.iloc[0]["date"] if len(recovery) > 0 else None
        dd_duration = (trough_date - peak_date).days

        results.append({
            "amfi_code": code,
            "max_drawdown_pct": round(max_dd * 100, 2),
            "dd_peak_date": peak_date.strftime("%Y-%m-%d"),
            "dd_trough_date": trough_date.strftime("%Y-%m-%d"),
            "dd_duration_days": dd_duration,
            "recovered": "Yes" if recovery_date else "No",
            "recovery_date": recovery_date.strftime("%Y-%m-%d") if recovery_date else None,
        })

    dd_df = pd.DataFrame(results)
    dd_df = dd_df.merge(fund[["amfi_code", "scheme_name", "sub_category"]],
                        on="amfi_code", how="left")
    dd_df = dd_df.sort_values("max_drawdown_pct")

    print(f"  Max Drawdown computed for {len(dd_df)} schemes")
    print(f"\n  Worst 5 Drawdowns:")
    for _, r in dd_df.head(5).iterrows():
        print(f"    {r['scheme_name'][:40]:<42} DD: {r['max_drawdown_pct']:>6}%  "
              f"({r['dd_peak_date']} -> {r['dd_trough_date']}, {r['dd_duration_days']}d)")

    return dd_df


# ============================================================================
# 7. FUND SCORECARD (0-100)
# ============================================================================
def compute_fund_scorecard(cagr_df, sharpe_df, sortino_df, ab_df, dd_df, fund):
    """
    Composite score: 30% × 3yr return rank + 25% × Sharpe rank
    + 20% × Alpha rank + 15% × expense ratio rank (inv) + 10% × max DD rank (inv)
    """
    header("7. Building Fund Scorecard (0-100)")

    # Start with fund master
    sc = fund[["amfi_code", "scheme_name", "fund_house", "sub_category", "plan",
               "expense_ratio_pct"]].copy()

    # Merge metrics
    sc = sc.merge(cagr_df[["amfi_code", "cagr_1yr", "cagr_3yr", "cagr_5yr"]],
                  on="amfi_code", how="left")
    sc = sc.merge(sharpe_df[["amfi_code", "sharpe_ratio", "mean_return_ann", "std_ann"]],
                  on="amfi_code", how="left")
    sc = sc.merge(sortino_df[["amfi_code", "sortino_ratio", "downside_std_ann", "pct_negative_days"]],
                  on="amfi_code", how="left")
    sc = sc.merge(ab_df[["amfi_code", "alpha_annual_pct", "beta", "r_squared"]],
                  on="amfi_code", how="left")
    sc = sc.merge(dd_df[["amfi_code", "max_drawdown_pct", "dd_peak_date", "dd_trough_date"]],
                  on="amfi_code", how="left")

    n = len(sc)

    # Rank each metric (1 = best for each)
    # Higher is better: 3yr return, sharpe, alpha
    sc["rank_return_3yr"] = sc["cagr_3yr"].rank(ascending=False, na_option="bottom")
    sc["rank_sharpe"] = sc["sharpe_ratio"].rank(ascending=False, na_option="bottom")
    sc["rank_alpha"] = sc["alpha_annual_pct"].rank(ascending=False, na_option="bottom")
    # Lower is better (inverse): expense ratio, max drawdown
    sc["rank_expense"] = sc["expense_ratio_pct"].rank(ascending=True, na_option="bottom")
    sc["rank_dd"] = sc["max_drawdown_pct"].rank(ascending=False, na_option="bottom")  # Less negative = better

    # Convert ranks to 0-100 score: score = (N - rank + 1) / N * 100
    for col in ["rank_return_3yr", "rank_sharpe", "rank_alpha", "rank_expense", "rank_dd"]:
        sc[col + "_score"] = ((n - sc[col] + 1) / n * 100).round(1)

    # Weighted composite
    sc["composite_score"] = (
        0.30 * sc["rank_return_3yr_score"] +
        0.25 * sc["rank_sharpe_score"] +
        0.20 * sc["rank_alpha_score"] +
        0.15 * sc["rank_expense_score"] +
        0.10 * sc["rank_dd_score"]
    ).round(1)

    sc["overall_rank"] = sc["composite_score"].rank(ascending=False).astype(int)
    sc = sc.sort_values("overall_rank")

    # Select output columns
    output_cols = [
        "overall_rank", "amfi_code", "scheme_name", "fund_house", "sub_category", "plan",
        "composite_score",
        "cagr_1yr", "cagr_3yr", "cagr_5yr",
        "sharpe_ratio", "sortino_ratio",
        "alpha_annual_pct", "beta", "r_squared",
        "max_drawdown_pct", "expense_ratio_pct",
        "mean_return_ann", "std_ann", "downside_std_ann", "pct_negative_days",
        "dd_peak_date", "dd_trough_date",
    ]
    sc_out = sc[[c for c in output_cols if c in sc.columns]]

    # Save
    sc_out.to_csv("fund_scorecard.csv", index=False)
    print(f"  Fund Scorecard computed for {len(sc_out)} schemes")
    print(f"  -> Saved: fund_scorecard.csv")
    print(f"\n  Weights: 3Y Return(30%) + Sharpe(25%) + Alpha(20%) + ExpenseRatio(15%) + MaxDD(10%)")
    print(f"\n  Top 10 Funds:")
    print(f"  {'Rank':<5} {'Scheme':<45} {'Score':>6} {'3Y%':>6} {'Sharpe':>7} {'Alpha%':>7}")
    print(f"  {'-'*78}")
    for _, r in sc_out.head(10).iterrows():
        print(f"  {r['overall_rank']:<5} {r['scheme_name'][:43]:<45} {r['composite_score']:>5.1f}"
              f"  {r.get('cagr_3yr',''):>5}  {r.get('sharpe_ratio',''):>6.3f}"
              f"  {r.get('alpha_annual_pct',''):>6}")

    # Scorecard bar chart
    top20 = sc_out.head(20).copy()
    top20["short_name"] = top20["scheme_name"].apply(lambda x: x.split(" - ")[0][:30])

    fig, ax = plt.subplots(figsize=(16, 10))
    colors = ["#1a73e8" if i >= 5 else "#34a853" if i >= 2 else "#ea4335"
              for i in range(len(top20))]
    colors.reverse()
    bars = ax.barh(top20["short_name"][::-1], top20["composite_score"][::-1],
                   color=colors, edgecolor="white", linewidth=1.5)

    for bar, score in zip(bars, top20["composite_score"][::-1]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{score:.1f}", va="center", fontsize=10, fontweight="bold")

    ax.set_title("Fund Scorecard — Top 20 Funds (Composite Score 0–100)\n"
                 "30% Return + 25% Sharpe + 20% Alpha + 15% Expense + 10% Drawdown",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Composite Score", fontsize=13)
    ax.set_xlim(0, 105)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "18_fund_scorecard.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  -> Saved: {CHARTS_DIR}/18_fund_scorecard.png")

    return sc_out


# ============================================================================
# 8. BENCHMARK COMPARISON (Top 5 vs Nifty 50 & Nifty 100)
# ============================================================================
def benchmark_comparison(nav_with_returns, fund, bench, scorecard):
    """Plot top 5 funds vs benchmarks. Compute tracking error."""
    header("8. Benchmark Comparison — Top 5 vs NIFTY 50 & NIFTY 100")

    # Get top 5 equity funds from scorecard
    equity_funds = scorecard.merge(fund[["amfi_code", "category"]], on="amfi_code", how="left")
    equity_funds = equity_funds[equity_funds["category"] == "Equity"]
    top5_codes = equity_funds.head(5)["amfi_code"].tolist()
    top5_names = equity_funds.head(5)["scheme_name"].tolist()

    # Use 3-year window from latest date
    latest = nav_with_returns["date"].max()
    start_3y = latest - pd.DateOffset(years=3)

    # Prepare fund NAVs (rebased to 100)
    fig = go.Figure()
    fund_returns_dict = {}

    for code, name in zip(top5_codes, top5_names):
        scheme = nav_with_returns[(nav_with_returns["amfi_code"] == code) &
                                  (nav_with_returns["date"] >= start_3y)].sort_values("date")
        if len(scheme) == 0:
            continue
        rebased = scheme["nav"] / scheme["nav"].iloc[0] * 100
        short_name = name.split(" - ")[0][:30]
        fig.add_trace(go.Scatter(x=scheme["date"], y=rebased,
                                  mode="lines", name=short_name,
                                  line=dict(width=2.5)))
        fund_returns_dict[code] = scheme[["date", "daily_return"]].set_index("date")["daily_return"]

    # Add benchmarks
    for idx_name, color, dash in [("NIFTY50", "#202124", "dash"), ("NIFTY100", "#607d8b", "dot")]:
        idx = bench[(bench["index_name"] == idx_name) &
                    (bench["date"] >= start_3y)].sort_values("date")
        if len(idx) == 0:
            continue
        rebased = idx["close_value"] / idx["close_value"].iloc[0] * 100
        fig.add_trace(go.Scatter(x=idx["date"], y=rebased,
                                  mode="lines", name=idx_name,
                                  line=dict(width=3, dash=dash, color=color)))

    fig.update_layout(
        title="Top 5 Funds vs NIFTY 50 & NIFTY 100 — 3-Year Comparison (Rebased to 100)",
        template="plotly_white", height=700,
        xaxis_title="Date", yaxis_title="Rebased Value (100 = Start)",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        title_font_size=17, font=dict(size=13),
    )

    # Save
    fig.write_html(os.path.join(CHARTS_DIR, "19_benchmark_comparison.html"))
    try:
        fig.write_image(os.path.join(CHARTS_DIR, "19_benchmark_comparison.png"),
                        width=1400, height=750, scale=2)
        print(f"  -> Saved: {CHARTS_DIR}/19_benchmark_comparison.png")
    except Exception:
        print(f"  -> Saved HTML: {CHARTS_DIR}/19_benchmark_comparison.html")

    # Compute Tracking Error
    print(f"\n  Tracking Error (vs NIFTY 100) — annualised:")

    nifty100 = bench[bench["index_name"] == "NIFTY100"].sort_values("date").copy()
    nifty100["bench_return"] = nifty100["close_value"].pct_change()
    bench_rets = nifty100[nifty100["date"] >= start_3y][["date", "bench_return"]].set_index("date")["bench_return"]

    te_results = []
    for code, name in zip(top5_codes, top5_names):
        if code not in fund_returns_dict:
            continue
        fund_ret = fund_returns_dict[code]
        merged = pd.DataFrame({"fund": fund_ret, "bench": bench_rets}).dropna()
        if len(merged) < 30:
            continue
        tracking_diff = merged["fund"] - merged["bench"]
        te = tracking_diff.std() * np.sqrt(TRADING_DAYS)
        te_results.append({"amfi_code": code, "scheme_name": name,
                          "tracking_error_pct": round(te * 100, 2)})
        short = name.split(" - ")[0][:40]
        print(f"    {short:<42} TE: {te*100:.2f}%")

    # Also create matplotlib version for reliable PNG
    fig_mpl, ax = plt.subplots(figsize=(16, 9))
    colors_mpl = PALETTE[:5] + ["#202124", "#607d8b"]

    ci = 0
    for code, name in zip(top5_codes, top5_names):
        scheme = nav_with_returns[(nav_with_returns["amfi_code"] == code) &
                                  (nav_with_returns["date"] >= start_3y)].sort_values("date")
        if len(scheme) == 0:
            continue
        rebased = scheme["nav"] / scheme["nav"].iloc[0] * 100
        short_name = name.split(" - ")[0][:25]
        ax.plot(scheme["date"], rebased, label=short_name, color=colors_mpl[ci], linewidth=2)
        ci += 1

    for idx_name, ls in [("NIFTY50", "--"), ("NIFTY100", ":")]:
        idx = bench[(bench["index_name"] == idx_name) &
                    (bench["date"] >= start_3y)].sort_values("date")
        if len(idx) == 0:
            continue
        rebased = idx["close_value"] / idx["close_value"].iloc[0] * 100
        ax.plot(idx["date"], rebased, label=idx_name, color=colors_mpl[ci],
                linewidth=3, linestyle=ls)
        ci += 1

    ax.set_title("Top 5 Funds vs NIFTY 50 & NIFTY 100 — 3-Year Comparison (Rebased to 100)",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Date", fontsize=13)
    ax.set_ylabel("Rebased Value (100 = Start)", fontsize=13)
    ax.legend(fontsize=10, loc="upper left")
    ax.axhline(y=100, color="gray", linestyle="-", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "19_benchmark_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> Saved: {CHARTS_DIR}/19_benchmark_comparison.png")

    return te_results


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n")
    header("BLUESTOCK FINTECH - DAY 4: PERFORMANCE ANALYTICS")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Risk-free rate: {RF_ANNUAL*100}% (RBI repo rate proxy)")
    sep()

    nav, fund, perf, bench = load_data()
    print(f"  NAV: {len(nav):,} rows | Funds: {len(fund)} | Benchmarks: {bench['index_name'].nunique()}")

    # 1. Daily Returns
    nav_ret = compute_daily_returns(nav)

    # 2. CAGR
    cagr_df = compute_cagr(nav_ret, fund)

    # 3. Sharpe
    sharpe_df = compute_sharpe(nav_ret, fund)

    # 4. Sortino
    sortino_df = compute_sortino(nav_ret, fund)

    # 5. Alpha & Beta
    ab_df = compute_alpha_beta(nav_ret, fund, bench)

    # 6. Max Drawdown
    dd_df = compute_max_drawdown(nav_ret, fund)

    # 7. Fund Scorecard
    scorecard = compute_fund_scorecard(cagr_df, sharpe_df, sortino_df, ab_df, dd_df, fund)

    # 8. Benchmark Comparison
    te_results = benchmark_comparison(nav_ret, fund, bench, scorecard)

    # Summary
    header("DAY 4 PERFORMANCE ANALYTICS COMPLETE")
    print(f"\n  Output files:")
    print(f"    fund_scorecard.csv       ({len(scorecard)} schemes)")
    print(f"    alpha_beta.csv           ({len(ab_df)} schemes)")
    print(f"  Charts:")
    for f in ["16_return_distribution.png", "17_alpha_beta_scatter.png",
              "18_fund_scorecard.png", "19_benchmark_comparison.png"]:
        path = os.path.join(CHARTS_DIR, f)
        if os.path.exists(path):
            print(f"    {f}")
    print(f"\n  Completed at {datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == "__main__":
    main()
