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
"""
=============================================================================
 Bluestock Fintech — Mutual Fund Capstone Project
 Day 2: Data Cleaning & Preprocessing

 Script: data_cleaning.py
 Purpose: Clean all 10 CSV datasets, apply validation rules, and save
          cleaned versions to data/processed/.
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
RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
REPORTS_DIR = "reports"

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def sep(char="=", n=80):
    print(char * n)


def header(title):
    sep()
    print(f"  {title}")
    sep()


def load_raw(filename):
    """Load a raw CSV from data/raw/."""
    return pd.read_csv(os.path.join(RAW_DIR, filename))


def save_cleaned(df, filename):
    """Save a cleaned DataFrame to data/processed/."""
    path = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  -> Saved: {path} ({len(df):,} rows x {df.shape[1]} cols)")
    return path


# ============================================================================
# 1. CLEAN: nav_history
# ============================================================================
def clean_nav_history():
    header("1/10  Cleaning: nav_history")

    df = load_raw("02_nav_history.csv")
    print(f"  Raw shape: {df.shape}")

    # 1a. Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = df["date"].isna().sum()
    if bad_dates > 0:
        print(f"  WARNING: {bad_dates} unparseable dates dropped")
        df = df.dropna(subset=["date"])

    # 1b. Remove exact duplicates on (amfi_code, date)
    before = len(df)
    df = df.drop_duplicates(subset=["amfi_code", "date"], keep="first")
    dupes_removed = before - len(df)
    print(f"  Duplicates removed: {dupes_removed}")

    # 1c. Validate NAV > 0
    invalid_nav = (df["nav"] <= 0).sum()
    if invalid_nav > 0:
        print(f"  WARNING: {invalid_nav} rows with NAV <= 0 removed")
        df = df[df["nav"] > 0]

    # 1d. Sort by amfi_code + date
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # 1e. Forward-fill missing NAV for holidays/weekends
    #     Reindex each scheme to full business-day calendar, then ffill
    schemes = df["amfi_code"].unique()
    global_min = df["date"].min()
    global_max = df["date"].max()
    bdays = pd.bdate_range(start=global_min, end=global_max)

    filled_frames = []
    total_filled = 0

    for code in schemes:
        chunk = df[df["amfi_code"] == code].set_index("date")
        chunk_reindexed = chunk.reindex(bdays)
        chunk_reindexed["amfi_code"] = code
        n_missing = chunk_reindexed["nav"].isna().sum()
        total_filled += n_missing
        chunk_reindexed["nav"] = chunk_reindexed["nav"].ffill()
        # Drop any remaining NaN at the very start (before first NAV)
        chunk_reindexed = chunk_reindexed.dropna(subset=["nav"])
        chunk_reindexed["amfi_code"] = chunk_reindexed["amfi_code"].astype(int)
        filled_frames.append(chunk_reindexed.reset_index().rename(columns={"index": "date"}))

    df_clean = pd.concat(filled_frames, ignore_index=True)
    df_clean["date"] = df_clean["date"].dt.strftime("%Y-%m-%d")
    print(f"  Business-day gaps forward-filled: {total_filled:,}")
    print(f"  Clean shape: {df_clean.shape}")

    save_cleaned(df_clean, "02_nav_history.csv")
    return df_clean


# ============================================================================
# 2. CLEAN: investor_transactions
# ============================================================================
def clean_investor_transactions():
    header("2/10  Cleaning: investor_transactions")

    df = load_raw("08_investor_transactions.csv")
    print(f"  Raw shape: {df.shape}")

    # 2a. Parse dates
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    bad_dates = df["transaction_date"].isna().sum()
    if bad_dates > 0:
        print(f"  WARNING: {bad_dates} unparseable dates dropped")
        df = df.dropna(subset=["transaction_date"])

    # 2b. Standardise transaction_type
    type_map = {
        "sip": "SIP", "Sip": "SIP", "SIP": "SIP",
        "lumpsum": "Lumpsum", "Lumpsum": "Lumpsum", "LUMPSUM": "Lumpsum", "lump_sum": "Lumpsum",
        "redemption": "Redemption", "Redemption": "Redemption", "REDEMPTION": "Redemption",
        "redeem": "Redemption", "Redeem": "Redemption",
    }
    df["transaction_type"] = df["transaction_type"].str.strip()
    original_types = df["transaction_type"].unique()
    df["transaction_type"] = df["transaction_type"].map(type_map).fillna(df["transaction_type"])
    valid_types = {"SIP", "Lumpsum", "Redemption"}
    invalid_types = set(df["transaction_type"].unique()) - valid_types
    if invalid_types:
        print(f"  WARNING: Non-standard transaction types found: {invalid_types}")
        df = df[df["transaction_type"].isin(valid_types)]
    print(f"  Transaction types: {original_types} -> {df['transaction_type'].unique()}")

    # 2c. Validate amount > 0
    invalid_amt = (df["amount_inr"] <= 0).sum()
    if invalid_amt > 0:
        print(f"  WARNING: {invalid_amt} rows with amount <= 0 removed")
        df = df[df["amount_inr"] > 0]

    # 2d. Validate KYC status enum
    valid_kyc = {"Verified", "Pending"}
    df["kyc_status"] = df["kyc_status"].str.strip().str.title()
    invalid_kyc = set(df["kyc_status"].unique()) - valid_kyc
    if invalid_kyc:
        print(f"  WARNING: Non-standard KYC values: {invalid_kyc}")
    print(f"  KYC status values: {df['kyc_status'].unique()}")

    # 2e. Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    print(f"  Duplicates removed: {before - len(df)}")

    # 2f. Format date
    df["transaction_date"] = df["transaction_date"].dt.strftime("%Y-%m-%d")
    df = df.sort_values(["transaction_date", "investor_id"]).reset_index(drop=True)
    print(f"  Clean shape: {df.shape}")

    save_cleaned(df, "08_investor_transactions.csv")
    return df


# ============================================================================
# 3. CLEAN: scheme_performance
# ============================================================================
def clean_scheme_performance():
    header("3/10  Cleaning: scheme_performance")

    df = load_raw("07_scheme_performance.csv")
    print(f"  Raw shape: {df.shape}")

    # 3a. Validate return columns are numeric
    return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                   "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio",
                   "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct"]
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        non_numeric = df[col].isna().sum()
        if non_numeric > 0:
            print(f"  WARNING: {col} has {non_numeric} non-numeric values (set to NaN)")

    # 3b. Flag expense_ratio anomalies (should be 0.1% - 2.5%)
    er = df["expense_ratio_pct"]
    anomalies = df[(er < 0.1) | (er > 2.5)]
    if len(anomalies) > 0:
        print(f"  ANOMALY: {len(anomalies)} schemes with expense_ratio outside [0.1%, 2.5%]:")
        for _, row in anomalies.iterrows():
            print(f"    - {row['amfi_code']} {row['scheme_name']}: {row['expense_ratio_pct']}%")
    else:
        print(f"  Expense ratio range: {er.min():.2f}% - {er.max():.2f}% (all valid)")

    # 3c. Validate morningstar_rating in [1, 5]
    mr = df["morningstar_rating"]
    bad_rating = df[(mr < 1) | (mr > 5)]
    if len(bad_rating) > 0:
        print(f"  ANOMALY: {len(bad_rating)} schemes with morningstar_rating outside [1, 5]")

    # 3d. Validate beta range (typically 0 - 1.5)
    beta_outliers = df[(df["beta"] < 0) | (df["beta"] > 2)]
    if len(beta_outliers) > 0:
        print(f"  ANOMALY: {len(beta_outliers)} schemes with beta outside [0, 2]")
    else:
        print(f"  Beta range: {df['beta'].min():.2f} - {df['beta'].max():.2f} (reasonable)")

    # 3e. Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["amfi_code"], keep="first")
    print(f"  Duplicates removed: {before - len(df)}")

    df = df.sort_values("amfi_code").reset_index(drop=True)
    print(f"  Clean shape: {df.shape}")

    save_cleaned(df, "07_scheme_performance.csv")
    return df


# ============================================================================
# 4. CLEAN: fund_master
# ============================================================================
def clean_fund_master():
    header("4/10  Cleaning: fund_master")

    df = load_raw("01_fund_master.csv")
    print(f"  Raw shape: {df.shape}")

    # Parse launch_date
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Strip whitespace from all string columns
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["amfi_code"], keep="first")
    print(f"  Duplicates removed: {before - len(df)}")

    df = df.sort_values("amfi_code").reset_index(drop=True)
    print(f"  Clean shape: {df.shape}")

    save_cleaned(df, "01_fund_master.csv")
    return df


# ============================================================================
# 5. CLEAN: aum_by_fund_house
# ============================================================================
def clean_aum():
    header("5/10  Cleaning: aum_by_fund_house")

    df = load_raw("03_aum_by_fund_house.csv")
    print(f"  Raw shape: {df.shape}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["fund_house"] = df["fund_house"].str.strip()

    before = len(df)
    df = df.drop_duplicates(subset=["date", "fund_house"], keep="first")
    print(f"  Duplicates removed: {before - len(df)}")

    # Validate AUM > 0
    invalid = (df["aum_crore"] <= 0).sum()
    if invalid > 0:
        print(f"  WARNING: {invalid} rows with AUM <= 0")

    df = df.sort_values(["date", "fund_house"]).reset_index(drop=True)
    print(f"  Clean shape: {df.shape}")

    save_cleaned(df, "03_aum_by_fund_house.csv")
    return df


# ============================================================================
# 6. CLEAN: monthly_sip_inflows
# ============================================================================
def clean_sip_inflows():
    header("6/10  Cleaning: monthly_sip_inflows")

    df = load_raw("04_monthly_sip_inflows.csv")
    print(f"  Raw shape: {df.shape}")

    # Parse month to date (first of month)
    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Compute yoy_growth_pct where missing (if we have 12+ months of data)
    missing_yoy = df["yoy_growth_pct"].isna().sum()
    if missing_yoy > 0:
        print(f"  Missing yoy_growth_pct: {missing_yoy} (expected for first 12 months)")
        # Calculate YoY from sip_inflow_crore where possible
        df_sorted = df.sort_values("month").reset_index(drop=True)
        for i in range(12, len(df_sorted)):
            if pd.isna(df_sorted.loc[i, "yoy_growth_pct"]):
                curr = df_sorted.loc[i, "sip_inflow_crore"]
                prev = df_sorted.loc[i - 12, "sip_inflow_crore"]
                if prev > 0:
                    df_sorted.loc[i, "yoy_growth_pct"] = round((curr - prev) / prev * 100, 2)
        df = df_sorted
        still_missing = df["yoy_growth_pct"].isna().sum()
        print(f"  Remaining missing yoy_growth_pct: {still_missing}")

    before = len(df)
    df = df.drop_duplicates(subset=["month"], keep="first")
    print(f"  Duplicates removed: {before - len(df)}")

    df = df.sort_values("month").reset_index(drop=True)
    print(f"  Clean shape: {df.shape}")

    save_cleaned(df, "04_monthly_sip_inflows.csv")
    return df


# ============================================================================
# 7. CLEAN: category_inflows
# ============================================================================
def clean_category_inflows():
    header("7/10  Cleaning: category_inflows")

    df = load_raw("05_category_inflows.csv")
    print(f"  Raw shape: {df.shape}")

    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["category"] = df["category"].str.strip()

    before = len(df)
    df = df.drop_duplicates(subset=["month", "category"], keep="first")
    print(f"  Duplicates removed: {before - len(df)}")

    df = df.sort_values(["month", "category"]).reset_index(drop=True)
    print(f"  Clean shape: {df.shape}")

    save_cleaned(df, "05_category_inflows.csv")
    return df


# ============================================================================
# 8. CLEAN: industry_folio_count
# ============================================================================
def clean_folio_count():
    header("8/10  Cleaning: industry_folio_count")

    df = load_raw("06_industry_folio_count.csv")
    print(f"  Raw shape: {df.shape}")

    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.strftime("%Y-%m-%d")

    before = len(df)
    df = df.drop_duplicates(subset=["month"], keep="first")
    print(f"  Duplicates removed: {before - len(df)}")

    df = df.sort_values("month").reset_index(drop=True)
    print(f"  Clean shape: {df.shape}")

    save_cleaned(df, "06_industry_folio_count.csv")
    return df


# ============================================================================
# 9. CLEAN: portfolio_holdings
# ============================================================================
def clean_portfolio_holdings():
    header("9/10  Cleaning: portfolio_holdings")

    df = load_raw("09_portfolio_holdings.csv")
    print(f"  Raw shape: {df.shape}")

    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["stock_symbol"] = df["stock_symbol"].str.strip()
    df["sector"] = df["sector"].str.strip()

    # Validate weight_pct in [0, 100]
    bad_wt = df[(df["weight_pct"] < 0) | (df["weight_pct"] > 100)]
    if len(bad_wt) > 0:
        print(f"  ANOMALY: {len(bad_wt)} holdings with weight outside [0%, 100%]")

    before = len(df)
    df = df.drop_duplicates(subset=["amfi_code", "stock_symbol", "portfolio_date"], keep="first")
    print(f"  Duplicates removed: {before - len(df)}")

    df = df.sort_values(["amfi_code", "weight_pct"], ascending=[True, False]).reset_index(drop=True)
    print(f"  Clean shape: {df.shape}")

    save_cleaned(df, "09_portfolio_holdings.csv")
    return df


# ============================================================================
# 10. CLEAN: benchmark_indices
# ============================================================================
def clean_benchmark_indices():
    header("10/10  Cleaning: benchmark_indices")

    df = load_raw("10_benchmark_indices.csv")
    print(f"  Raw shape: {df.shape}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = df["date"].isna().sum()
    if bad_dates > 0:
        print(f"  WARNING: {bad_dates} unparseable dates dropped")
        df = df.dropna(subset=["date"])

    # Validate close_value > 0
    invalid = (df["close_value"] <= 0).sum()
    if invalid > 0:
        print(f"  WARNING: {invalid} rows with close_value <= 0 removed")
        df = df[df["close_value"] > 0]

    before = len(df)
    df = df.drop_duplicates(subset=["date", "index_name"], keep="first")
    print(f"  Duplicates removed: {before - len(df)}")

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df = df.sort_values(["index_name", "date"]).reset_index(drop=True)
    print(f"  Clean shape: {df.shape}")

    save_cleaned(df, "10_benchmark_indices.csv")
    return df


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n")
    header("BLUESTOCK FINTECH - DAY 2: DATA CLEANING & PREPROCESSING")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Input:  {os.path.abspath(RAW_DIR)}")
    print(f"  Output: {os.path.abspath(PROCESSED_DIR)}")
    sep()

    results = {}

    # Clean all 10 datasets
    results["nav_history"] = clean_nav_history()
    results["investor_transactions"] = clean_investor_transactions()
    results["scheme_performance"] = clean_scheme_performance()
    results["fund_master"] = clean_fund_master()
    results["aum_by_fund_house"] = clean_aum()
    results["monthly_sip_inflows"] = clean_sip_inflows()
    results["category_inflows"] = clean_category_inflows()
    results["industry_folio_count"] = clean_folio_count()
    results["portfolio_holdings"] = clean_portfolio_holdings()
    results["benchmark_indices"] = clean_benchmark_indices()

    # Summary
    header("CLEANING SUMMARY")
    print(f"\n  {'Dataset':<30} {'Raw Rows':>10} {'Clean Rows':>12}")
    print(f"  {'-'*55}")

    raw_files = {
        "fund_master": "01_fund_master.csv",
        "nav_history": "02_nav_history.csv",
        "aum_by_fund_house": "03_aum_by_fund_house.csv",
        "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
        "category_inflows": "05_category_inflows.csv",
        "industry_folio_count": "06_industry_folio_count.csv",
        "scheme_performance": "07_scheme_performance.csv",
        "investor_transactions": "08_investor_transactions.csv",
        "portfolio_holdings": "09_portfolio_holdings.csv",
        "benchmark_indices": "10_benchmark_indices.csv",
    }

    for name, df_clean in results.items():
        raw_df = load_raw(raw_files[name])
        print(f"  {name:<30} {len(raw_df):>10,} {len(df_clean):>12,}")

    total_clean = sum(len(df) for df in results.values())
    print(f"  {'-'*55}")
    print(f"  {'TOTAL':<30} {'':>10} {total_clean:>12,}")

    header("DAY 2 DATA CLEANING COMPLETE")
    print(f"\n  10 cleaned CSVs saved to: {os.path.abspath(PROCESSED_DIR)}")
    print(f"  Completed at {datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == "__main__":
    main()
"""
=============================================================================
 Bluestock Fintech — Mutual Fund Capstone Project
 Day 2: Database Loader

 Script: db_loader.py
 Purpose: Create SQLite database with star schema, load all cleaned
          datasets, generate dim_date, and verify row counts.
=============================================================================
"""

import os
import sys
import io
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine, text

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROCESSED_DIR = os.path.join("data", "processed")
DB_PATH = "data/db/bluestock_mf.db"
SCHEMA_PATH = os.path.join("sql", "schema.sql")
QUERIES_PATH = os.path.join("sql", "queries.sql")


def sep(char="=", n=80):
    print(char * n)


def header(title):
    sep()
    print(f"  {title}")
    sep()


# ---------------------------------------------------------------------------
# Generate dim_date dimension table
# ---------------------------------------------------------------------------
def generate_dim_date(start_date="2000-01-01", end_date="2027-12-31"):
    """Generate a comprehensive date dimension table."""
    print("\n  Generating dim_date dimension table...")

    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    df = pd.DataFrame({"date_key": dates})

    df["year"] = df["date_key"].dt.year
    df["quarter"] = df["date_key"].dt.quarter
    df["month"] = df["date_key"].dt.month
    df["month_name"] = df["date_key"].dt.strftime("%B")
    df["day"] = df["date_key"].dt.day
    df["day_of_week"] = df["date_key"].dt.dayofweek          # 0=Mon, 6=Sun
    df["day_name"] = df["date_key"].dt.strftime("%A")
    df["week_of_year"] = df["date_key"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_month_end"] = df["date_key"].dt.is_month_end.astype(int)
    df["is_quarter_end"] = df["date_key"].dt.is_quarter_end.astype(int)

    # Indian fiscal year (Apr-Mar): FY2024 = Apr 2023 – Mar 2024
    df["fiscal_year"] = df.apply(
        lambda r: r["year"] + 1 if r["month"] >= 4 else r["year"], axis=1
    )

    df["date_key"] = df["date_key"].dt.strftime("%Y-%m-%d")

    print(f"  -> dim_date: {len(df):,} rows ({start_date} to {end_date})")
    return df


# ---------------------------------------------------------------------------
# Load cleaned CSV
# ---------------------------------------------------------------------------
def load_cleaned(filename):
    """Load a cleaned CSV from data/processed/."""
    path = os.path.join(PROCESSED_DIR, filename)
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n")
    header("BLUESTOCK FINTECH - DAY 2: DATABASE LOADER")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Database: {os.path.abspath(DB_PATH)}")
    print(f"  Schema: {os.path.abspath(SCHEMA_PATH)}")
    sep()

    # Remove existing DB if present
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"\n  Removed existing database: {DB_PATH}")

    # Create SQLAlchemy engine
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

    # -----------------------------------------------------------------------
    # Step 1: Execute schema.sql
    # -----------------------------------------------------------------------
    header("Step 1: Creating Schema")
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()

    with engine.connect() as conn:
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
        for stmt in statements:
            # Skip indexes and comments — indexes will be created after data loading
            if stmt and not stmt.startswith("--") and "CREATE INDEX" not in stmt.upper():
                conn.execute(text(stmt))
        conn.commit()
    print("  Schema (tables) created successfully!")

    # -----------------------------------------------------------------------
    # Step 2: Generate and load dim_date
    # -----------------------------------------------------------------------
    header("Step 2: Loading Dimension Tables")

    # dim_date
    df_dim_date = generate_dim_date()
    df_dim_date.to_sql("dim_date", engine, if_exists="replace", index=False)
    print(f"  -> dim_date loaded: {len(df_dim_date):,} rows")

    # dim_fund (from cleaned fund_master)
    df_fund = load_cleaned("01_fund_master.csv")
    df_fund.to_sql("dim_fund", engine, if_exists="replace", index=False)
    print(f"  -> dim_fund loaded: {len(df_fund):,} rows")

    # -----------------------------------------------------------------------
    # Step 3: Load Fact Tables
    # -----------------------------------------------------------------------
    header("Step 3: Loading Fact Tables")

    # fact_nav
    df_nav = load_cleaned("02_nav_history.csv")
    df_nav.to_sql("fact_nav", engine, if_exists="replace", index=False)
    print(f"  -> fact_nav loaded: {len(df_nav):,} rows")

    # fact_transactions (without auto-increment txn_id; let SQLite handle it)
    df_txn = load_cleaned("08_investor_transactions.csv")
    # Drop txn_id if present to let autoincrement work
    if "txn_id" in df_txn.columns:
        df_txn = df_txn.drop(columns=["txn_id"])
    df_txn.to_sql("fact_transactions", engine, if_exists="replace", index=False)
    print(f"  -> fact_transactions loaded: {len(df_txn):,} rows")

    # fact_performance
    df_perf = load_cleaned("07_scheme_performance.csv")
    df_perf.to_sql("fact_performance", engine, if_exists="replace", index=False)
    print(f"  -> fact_performance loaded: {len(df_perf):,} rows")

    # fact_aum
    df_aum = load_cleaned("03_aum_by_fund_house.csv")
    df_aum.to_sql("fact_aum", engine, if_exists="replace", index=False)
    print(f"  -> fact_aum loaded: {len(df_aum):,} rows")

    # fact_sip_inflows
    df_sip = load_cleaned("04_monthly_sip_inflows.csv")
    df_sip.to_sql("fact_sip_inflows", engine, if_exists="replace", index=False)
    print(f"  -> fact_sip_inflows loaded: {len(df_sip):,} rows")

    # fact_category_inflows
    df_cat = load_cleaned("05_category_inflows.csv")
    df_cat.to_sql("fact_category_inflows", engine, if_exists="replace", index=False)
    print(f"  -> fact_category_inflows loaded: {len(df_cat):,} rows")

    # -----------------------------------------------------------------------
    # Step 4: Load Additional Tables
    # -----------------------------------------------------------------------
    header("Step 4: Loading Additional Tables")

    df_folio = load_cleaned("06_industry_folio_count.csv")
    df_folio.to_sql("industry_folio_count", engine, if_exists="replace", index=False)
    print(f"  -> industry_folio_count loaded: {len(df_folio):,} rows")

    df_hold = load_cleaned("09_portfolio_holdings.csv")
    df_hold.to_sql("portfolio_holdings", engine, if_exists="replace", index=False)
    print(f"  -> portfolio_holdings loaded: {len(df_hold):,} rows")

    df_bench = load_cleaned("10_benchmark_indices.csv")
    df_bench.to_sql("benchmark_indices", engine, if_exists="replace", index=False)
    print(f"  -> benchmark_indices loaded: {len(df_bench):,} rows")

    # -----------------------------------------------------------------------
    # Step 5: Create Indexes
    # -----------------------------------------------------------------------
    header("Step 5: Creating Indexes")

    with open(SCHEMA_PATH, "r") as f:
        schema_sql_idx = f.read()

    with engine.connect() as conn:
        statements = [s.strip() for s in schema_sql_idx.split(";") if s.strip()]
        idx_count = 0
        for stmt in statements:
            if "CREATE INDEX" in stmt.upper():
                conn.execute(text(stmt))
                idx_count += 1
        conn.commit()
    print(f"  {idx_count} indexes created successfully!")

    # -----------------------------------------------------------------------
    # Step 6: Verify Row Counts
    # -----------------------------------------------------------------------
    header("Step 6: Row Count Verification")

    expected = {
        "dim_date": len(df_dim_date),
        "dim_fund": len(df_fund),
        "fact_nav": len(df_nav),
        "fact_transactions": len(df_txn),
        "fact_performance": len(df_perf),
        "fact_aum": len(df_aum),
        "fact_sip_inflows": len(df_sip),
        "fact_category_inflows": len(df_cat),
        "industry_folio_count": len(df_folio),
        "portfolio_holdings": len(df_hold),
        "benchmark_indices": len(df_bench),
    }

    all_ok = True
    print(f"\n  {'Table':<30} {'Expected':>10} {'Actual':>10} {'Status':>10}")
    print(f"  {'-'*65}")

    with engine.connect() as conn:
        for table, exp_count in expected.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            actual = result.scalar()
            status = "OK" if actual == exp_count else "MISMATCH"
            if status != "OK":
                all_ok = False
            icon = "  " if status == "OK" else "!!"
            print(f"  {table:<30} {exp_count:>10,} {actual:>10,} {icon:>2} {status}")

    # -----------------------------------------------------------------------
    # Step 7: Run Sample Queries
    # -----------------------------------------------------------------------
    header("Step 7: Testing Analytical Queries")

    # Read queries.sql and split into individual queries
    with open(QUERIES_PATH, "r") as f:
        queries_sql = f.read()

    # Split on the separator pattern
    import re
    query_blocks = re.split(r'-- =+\n-- QUERY \d+:', queries_sql)

    # Parse each query block
    queries = []
    for block in query_blocks[1:]:  # skip preamble
        lines = block.strip().split("\n")
        # Extract title from first line
        title = lines[0].strip().rstrip("=").rstrip("-").strip()
        # Find SQL (everything after the last -- === line)
        sql_lines = []
        in_sql = False
        for line in lines:
            if line.startswith("SELECT") or in_sql:
                in_sql = True
                sql_lines.append(line)
        sql = "\n".join(sql_lines).rstrip(";")
        if sql.strip():
            queries.append((title, sql))

    with engine.connect() as conn:
        for i, (title, sql) in enumerate(queries, 1):
            try:
                result = pd.read_sql(sql, conn)
                print(f"\n  Query {i}: {title[:60]}")
                print(f"  Returned: {len(result)} rows x {result.shape[1]} columns")
                if len(result) > 0:
                    # Show first 3 rows
                    print(result.head(3).to_string(index=False, max_colwidth=30))
            except Exception as e:
                print(f"\n  Query {i}: {title[:60]}")
                print(f"  ERROR: {str(e)}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    header("DATABASE LOADING COMPLETE")
    db_size = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"\n  Database: {os.path.abspath(DB_PATH)}")
    print(f"  Size: {db_size:.2f} MB")
    print(f"  Tables: {len(expected)}")
    total_rows = sum(expected.values())
    print(f"  Total rows: {total_rows:,}")
    print(f"  Verification: {'ALL PASSED' if all_ok else 'ISSUES FOUND'}")
    print(f"  Queries tested: {len(queries)}")
    print(f"  Completed at {datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == "__main__":
    main()
