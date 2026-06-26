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
