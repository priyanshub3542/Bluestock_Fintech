"""
=============================================================================
 Bluestock Fintech — Mutual Fund Capstone Project
 Day 1: Data Ingestion & Exploration
 
 Script: data_ingestion.py
 Purpose: Load all 10 CSV datasets, explore structure, validate AMFI codes,
          and generate a data quality summary report.
=============================================================================
"""

import os
import sys
import io
import pandas as pd
import numpy as np
from datetime import datetime

# Fix Windows console encoding for Unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_DATA_DIR = os.path.join("data", "raw")
REPORTS_DIR = "reports"

# All 10 datasets with their filenames and descriptions
DATASETS = {
    "fund_master":          ("01_fund_master.csv",          "Fund Master — Scheme Metadata"),
    "nav_history":          ("02_nav_history.csv",          "NAV History — Daily NAV Values"),
    "aum_by_fund_house":    ("03_aum_by_fund_house.csv",    "AUM by Fund House — Quarterly"),
    "monthly_sip_inflows":  ("04_monthly_sip_inflows.csv",  "Monthly SIP Inflows"),
    "category_inflows":     ("05_category_inflows.csv",     "Category-wise Net Inflows"),
    "industry_folio_count": ("06_industry_folio_count.csv",  "Industry Folio Count Growth"),
    "scheme_performance":   ("07_scheme_performance.csv",    "Scheme Performance Metrics"),
    "investor_transactions":("08_investor_transactions.csv", "Investor Transactions"),
    "portfolio_holdings":   ("09_portfolio_holdings.csv",    "Portfolio Holdings"),
    "benchmark_indices":    ("10_benchmark_indices.csv",     "Benchmark Index Daily Close"),
}


def print_separator(char="=", length=80):
    """Print a visual separator line."""
    print(char * length)


def print_header(title):
    """Print a formatted section header."""
    print_separator()
    print(f"  {title}")
    print_separator()


# ---------------------------------------------------------------------------
# TASK 1: Load all 10 CSV datasets
# ---------------------------------------------------------------------------
def load_all_datasets():
    """
    Load all 10 CSV datasets from data/raw/.
    Returns a dictionary of {name: DataFrame}.
    """
    print_header("TASK 1: Loading All 10 CSV Datasets")
    
    dataframes = {}
    
    for name, (filename, description) in DATASETS.items():
        filepath = os.path.join(RAW_DATA_DIR, filename)
        
        print(f"\n{'─' * 70}")
        print(f"📄 Loading: {filename}")
        print(f"   Description: {description}")
        print(f"   Path: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            dataframes[name] = df
            
            # Print .shape
            print(f"\n   📐 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Print .dtypes
            print(f"\n   📊 Data Types:")
            for col, dtype in df.dtypes.items():
                print(f"      • {col}: {dtype}")
            
            # Print .head()
            print(f"\n   👀 First 5 Rows:")
            print(df.head().to_string(index=True, max_colwidth=40))
            
            # Note anomalies
            null_counts = df.isnull().sum()
            total_nulls = null_counts.sum()
            dup_count = df.duplicated().sum()
            
            print(f"\n   ⚠️  Anomaly Check:")
            if total_nulls > 0:
                print(f"      🔴 Missing values found ({total_nulls} total):")
                for col in null_counts[null_counts > 0].index:
                    print(f"         • {col}: {null_counts[col]} missing ({null_counts[col]/len(df)*100:.1f}%)")
            else:
                print(f"      🟢 No missing values")
            
            if dup_count > 0:
                print(f"      🔴 Duplicate rows: {dup_count}")
            else:
                print(f"      🟢 No duplicate rows")
                
        except FileNotFoundError:
            print(f"   ❌ ERROR: File not found at {filepath}")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
    
    print(f"\n\n✅ Successfully loaded {len(dataframes)}/{len(DATASETS)} datasets")
    return dataframes


# ---------------------------------------------------------------------------
# TASK 2: Explore Fund Master
# ---------------------------------------------------------------------------
def explore_fund_master(df_fund_master):
    """
    Explore the fund_master dataset in detail:
    - Unique fund houses, categories, sub-categories, risk grades
    - AMFI scheme code structure analysis
    """
    print_header("TASK 2: Exploring Fund Master")
    
    df = df_fund_master
    
    # Unique Fund Houses
    fund_houses = df["fund_house"].unique()
    print(f"\n🏢 Unique Fund Houses ({len(fund_houses)}):")
    for i, fh in enumerate(sorted(fund_houses), 1):
        count = len(df[df["fund_house"] == fh])
        print(f"   {i:2d}. {fh} ({count} schemes)")
    
    # Unique Categories
    categories = df["category"].unique()
    print(f"\n📂 Unique Categories ({len(categories)}):")
    for cat in sorted(categories):
        count = len(df[df["category"] == cat])
        print(f"   • {cat} ({count} schemes)")
    
    # Unique Sub-Categories
    sub_categories = df["sub_category"].unique()
    print(f"\n📁 Unique Sub-Categories ({len(sub_categories)}):")
    for sub in sorted(sub_categories):
        count = len(df[df["sub_category"] == sub])
        print(f"   • {sub} ({count} schemes)")
    
    # Risk Grades
    risk_grades = df["risk_category"].unique()
    print(f"\n⚡ Risk Grades ({len(risk_grades)}):")
    for risk in sorted(risk_grades):
        count = len(df[df["risk_category"] == risk])
        print(f"   • {risk} ({count} schemes)")
    
    # Plan Types
    plans = df["plan"].unique()
    print(f"\n📋 Plan Types ({len(plans)}):")
    for plan in sorted(plans):
        count = len(df[df["plan"] == plan])
        print(f"   • {plan} ({count} schemes)")
    
    # AMFI Scheme Code Structure
    print(f"\n🔢 AMFI Scheme Code Structure:")
    amfi_codes = df["amfi_code"].values
    print(f"   • Total codes: {len(amfi_codes)}")
    print(f"   • Unique codes: {len(set(amfi_codes))}")
    print(f"   • Min code: {min(amfi_codes)}")
    print(f"   • Max code: {max(amfi_codes)}")
    print(f"   • Code range: {min(amfi_codes)} – {max(amfi_codes)}")
    
    # Code digit analysis
    code_lengths = [len(str(c)) for c in amfi_codes]
    print(f"   • Code lengths: {sorted(set(code_lengths))} digits")
    
    # SEBI Category Codes
    if "sebi_category_code" in df.columns:
        sebi_codes = df["sebi_category_code"].unique()
        print(f"\n📜 SEBI Category Codes ({len(sebi_codes)}):")
        for code in sorted(sebi_codes):
            schemes = df[df["sebi_category_code"] == code]["sub_category"].unique()
            print(f"   • {code}: {', '.join(schemes)}")
    
    # Fund Manager analysis
    if "fund_manager" in df.columns:
        managers = df["fund_manager"].unique()
        print(f"\n👤 Unique Fund Managers: {len(managers)}")
        for mgr in sorted(managers):
            schemes = df[df["fund_manager"] == mgr]["scheme_name"].tolist()
            print(f"   • {mgr} → {len(schemes)} scheme(s)")


# ---------------------------------------------------------------------------
# TASK 3: Validate AMFI Codes
# ---------------------------------------------------------------------------
def validate_amfi_codes(df_fund_master, df_nav_history):
    """
    Cross-validate AMFI codes between fund_master and nav_history.
    Confirm every code in fund_master exists in nav_history.
    """
    print_header("TASK 3: AMFI Code Cross-Validation")
    
    master_codes = set(df_fund_master["amfi_code"].unique())
    nav_codes = set(df_nav_history["amfi_code"].unique())
    
    print(f"\n📊 AMFI Code Summary:")
    print(f"   • Fund Master codes: {len(master_codes)}")
    print(f"   • NAV History codes: {len(nav_codes)}")
    
    # Codes in master but not in nav
    missing_in_nav = master_codes - nav_codes
    print(f"\n🔍 Codes in Fund Master but NOT in NAV History: {len(missing_in_nav)}")
    if missing_in_nav:
        for code in sorted(missing_in_nav):
            scheme = df_fund_master[df_fund_master["amfi_code"] == code]["scheme_name"].values[0]
            print(f"   ❌ {code} → {scheme}")
    else:
        print(f"   ✅ All fund master codes exist in NAV history!")
    
    # Codes in nav but not in master
    extra_in_nav = nav_codes - master_codes
    print(f"\n🔍 Codes in NAV History but NOT in Fund Master: {len(extra_in_nav)}")
    if extra_in_nav:
        for code in sorted(extra_in_nav):
            nav_count = len(df_nav_history[df_nav_history["amfi_code"] == code])
            print(f"   ⚠️  {code} → {nav_count} NAV records (no master entry)")
    else:
        print(f"   ✅ All NAV history codes are in fund master!")
    
    # Common codes
    common_codes = master_codes & nav_codes
    print(f"\n✅ Common Codes (matched): {len(common_codes)}")
    
    # NAV coverage per scheme
    print(f"\n📅 NAV Date Coverage per Scheme:")
    for code in sorted(common_codes):
        scheme_navs = df_nav_history[df_nav_history["amfi_code"] == code]
        scheme_name = df_fund_master[df_fund_master["amfi_code"] == code]["scheme_name"].values[0]
        min_date = scheme_navs["date"].min()
        max_date = scheme_navs["date"].max()
        count = len(scheme_navs)
        # Truncate scheme name for clean output
        short_name = scheme_name[:45] + "..." if len(scheme_name) > 45 else scheme_name
        print(f"   • {code} | {short_name:<48} | {min_date} to {max_date} | {count:,} records")
    
    return missing_in_nav, extra_in_nav, common_codes


# ---------------------------------------------------------------------------
# TASK 4: Generate Data Quality Summary Report
# ---------------------------------------------------------------------------
def generate_quality_report(dataframes, missing_in_nav, extra_in_nav, common_codes):
    """
    Generate a comprehensive data quality summary and save to reports/.
    """
    print_header("TASK 4: Generating Data Quality Summary Report")
    
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(REPORTS_DIR, "data_quality_summary.txt")
    
    lines = []
    lines.append("=" * 80)
    lines.append("  BLUESTOCK FINTECH — MUTUAL FUND CAPSTONE PROJECT")
    lines.append("  DATA QUALITY SUMMARY REPORT")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    
    # ---- Overview ----
    lines.append("\n" + "─" * 80)
    lines.append("1. DATASET OVERVIEW")
    lines.append("─" * 80)
    lines.append(f"{'Dataset':<30} {'Rows':>8} {'Cols':>6} {'Nulls':>8} {'Dupes':>8} {'Size':>10}")
    lines.append("-" * 80)
    
    total_rows = 0
    total_nulls = 0
    total_dupes = 0
    
    for name, df in dataframes.items():
        rows = df.shape[0]
        cols = df.shape[1]
        nulls = df.isnull().sum().sum()
        dupes = df.duplicated().sum()
        size = f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB"
        
        total_rows += rows
        total_nulls += nulls
        total_dupes += dupes
        
        lines.append(f"{name:<30} {rows:>8,} {cols:>6} {nulls:>8} {dupes:>8} {size:>10}")
    
    lines.append("-" * 80)
    lines.append(f"{'TOTAL':<30} {total_rows:>8,} {'':>6} {total_nulls:>8} {total_dupes:>8}")
    
    # ---- Missing Values Detail ----
    lines.append("\n" + "─" * 80)
    lines.append("2. MISSING VALUES DETAIL")
    lines.append("─" * 80)
    
    has_missing = False
    for name, df in dataframes.items():
        null_cols = df.columns[df.isnull().any()]
        if len(null_cols) > 0:
            has_missing = True
            lines.append(f"\n  {name}:")
            for col in null_cols:
                null_count = df[col].isnull().sum()
                pct = null_count / len(df) * 100
                lines.append(f"    • {col}: {null_count} missing ({pct:.1f}%)")
    
    if not has_missing:
        lines.append("  ✅ No missing values found in any dataset.")
    
    # ---- Data Type Summary ----
    lines.append("\n" + "─" * 80)
    lines.append("3. DATA TYPE SUMMARY")
    lines.append("─" * 80)
    
    for name, df in dataframes.items():
        lines.append(f"\n  {name}:")
        for col, dtype in df.dtypes.items():
            lines.append(f"    • {col}: {dtype}")
    
    # ---- AMFI Code Validation ----
    lines.append("\n" + "─" * 80)
    lines.append("4. AMFI CODE CROSS-VALIDATION")
    lines.append("─" * 80)
    lines.append(f"  Fund Master codes:       {len(dataframes['fund_master']['amfi_code'].unique())}")
    lines.append(f"  NAV History codes:       {len(dataframes['nav_history']['amfi_code'].unique())}")
    lines.append(f"  Common (matched) codes:  {len(common_codes)}")
    lines.append(f"  Missing in NAV History:  {len(missing_in_nav)}")
    lines.append(f"  Extra in NAV History:    {len(extra_in_nav)}")
    
    if missing_in_nav:
        lines.append(f"\n  ❌ Codes in Fund Master but NOT in NAV History:")
        for code in sorted(missing_in_nav):
            scheme = dataframes['fund_master'][dataframes['fund_master']['amfi_code'] == code]['scheme_name'].values[0]
            lines.append(f"     {code} → {scheme}")
    
    if extra_in_nav:
        lines.append(f"\n  ⚠️  Codes in NAV History but NOT in Fund Master:")
        for code in sorted(extra_in_nav):
            nav_count = len(dataframes['nav_history'][dataframes['nav_history']['amfi_code'] == code])
            lines.append(f"     {code} → {nav_count} NAV records")
    
    if not missing_in_nav and not extra_in_nav:
        lines.append("  ✅ Perfect match — all AMFI codes are consistent across datasets.")
    
    # ---- Key Observations ----
    lines.append("\n" + "─" * 80)
    lines.append("5. KEY OBSERVATIONS & ANOMALIES")
    lines.append("─" * 80)
    
    # Check date ranges in nav_history
    df_nav = dataframes["nav_history"]
    lines.append(f"\n  NAV History Date Range: {df_nav['date'].min()} to {df_nav['date'].max()}")
    
    # Check for negative NAVs
    neg_navs = df_nav[df_nav["nav"] < 0] if "nav" in df_nav.columns else pd.DataFrame()
    lines.append(f"  Negative NAV values: {len(neg_navs)}")
    
    # Transaction summary
    if "investor_transactions" in dataframes:
        df_txn = dataframes["investor_transactions"]
        lines.append(f"\n  Investor Transactions:")
        lines.append(f"    • Unique investors: {df_txn['investor_id'].nunique()}")
        lines.append(f"    • Transaction types: {', '.join(df_txn['transaction_type'].unique())}")
        lines.append(f"    • Date range: {df_txn['transaction_date'].min()} to {df_txn['transaction_date'].max()}")
        if "amount_inr" in df_txn.columns:
            lines.append(f"    • Amount range: ₹{df_txn['amount_inr'].min():,.0f} to ₹{df_txn['amount_inr'].max():,.0f}")
    
    # Benchmark indices
    if "benchmark_indices" in dataframes:
        df_bm = dataframes["benchmark_indices"]
        lines.append(f"\n  Benchmark Indices:")
        lines.append(f"    • Indices tracked: {', '.join(df_bm['index_name'].unique())}")
        lines.append(f"    • Date range: {df_bm['date'].min()} to {df_bm['date'].max()}")
    
    # ---- Conclusion ----
    lines.append("\n" + "─" * 80)
    lines.append("6. CONCLUSION")
    lines.append("─" * 80)
    lines.append(f"  Total datasets loaded: {len(dataframes)}/10")
    lines.append(f"  Total records: {total_rows:,}")
    lines.append(f"  Total missing values: {total_nulls}")
    lines.append(f"  Total duplicate rows: {total_dupes}")
    lines.append(f"  AMFI code integrity: {'PASS ✅' if not missing_in_nav else 'ISSUES FOUND ⚠️'}")
    lines.append(f"  Overall data quality: {'GOOD ✅' if total_nulls < 100 and total_dupes == 0 else 'NEEDS ATTENTION ⚠️'}")
    lines.append("\n" + "=" * 80)
    lines.append("  END OF REPORT")
    lines.append("=" * 80)
    
    # Write report
    report_content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"\n✅ Data quality report saved to: {report_path}")
    print(f"\n--- Report Preview ---")
    print(report_content)
    
    return report_path


# ---------------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------------
def main():
    """Main execution flow for Day 1 data ingestion."""
    print("\n")
    print_header("BLUESTOCK FINTECH — DAY 1: DATA INGESTION & EXPLORATION")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Raw Data Directory: {os.path.abspath(RAW_DATA_DIR)}")
    print_separator()
    
    # Task 1: Load all datasets
    dataframes = load_all_datasets()
    
    # Task 2: Explore fund master
    if "fund_master" in dataframes:
        explore_fund_master(dataframes["fund_master"])
    
    # Task 3: Validate AMFI codes
    if "fund_master" in dataframes and "nav_history" in dataframes:
        missing_in_nav, extra_in_nav, common_codes = validate_amfi_codes(
            dataframes["fund_master"], dataframes["nav_history"]
        )
    else:
        missing_in_nav, extra_in_nav, common_codes = set(), set(), set()
    
    # Task 4: Generate data quality report
    generate_quality_report(dataframes, missing_in_nav, extra_in_nav, common_codes)
    
    print_header("DAY 1 DATA INGESTION COMPLETE ✅")
    print(f"\n  📊 Loaded {len(dataframes)} datasets")
    print(f"  📝 Report saved to reports/data_quality_summary.txt")
    print(f"  🕐 Completed at {datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == "__main__":
    main()
