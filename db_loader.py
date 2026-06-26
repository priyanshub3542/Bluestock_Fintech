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
DB_PATH = "bluestock_mf.db"
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
