"""
=============================================================================
 Bluestock Fintech — Mutual Fund Capstone Project
 Day 1: Live NAV Fetcher
 
 Script: live_nav_fetch.py
 Purpose: Fetch live NAV data from MFAPI (https://api.mfapi.in) for key
          mutual fund schemes and save as CSV files.
=============================================================================
"""

import os
import sys
import io
import json
import requests
import pandas as pd
from datetime import datetime

# Fix Windows console encoding for Unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_DATA_DIR = os.path.join("data", "raw")

# API base URL
MFAPI_BASE_URL = "https://api.mfapi.in/mf"

# Schemes to fetch — {AMFI_Code: Scheme_Name}
SCHEMES = {
    125497: "HDFC Top 100 Fund - Direct Plan - Growth",
    119551: "SBI Bluechip Fund - Regular Plan - Growth",
    120503: "ICICI Pru Bluechip Fund - Regular - Growth",
    118632: "Nippon India Large Cap Fund - Regular - Growth",
    119092: "Axis Bluechip Fund - Regular - Growth",
    120841: "Kotak Bluechip Fund - Regular - Growth",
}


def print_separator(char="=", length=80):
    """Print a visual separator line."""
    print(char * length)


def print_header(title):
    """Print a formatted section header."""
    print_separator()
    print(f"  {title}")
    print_separator()


def fetch_nav_data(scheme_code):
    """
    Fetch NAV data for a given AMFI scheme code from MFAPI.
    
    API Endpoint: GET https://api.mfapi.in/mf/{scheme_code}
    
    Returns:
        tuple: (meta_dict, nav_dataframe) or (None, None) on failure
    
    Response JSON structure:
        {
            "meta": {
                "fund_house": "...",
                "scheme_type": "...",
                "scheme_category": "...",
                "scheme_code": 123456,
                "scheme_name": "..."
            },
            "data": [
                {"date": "26-06-2026", "nav": "123.4567"},
                ...
            ],
            "status": "SUCCESS"
        }
    """
    url = f"{MFAPI_BASE_URL}/{scheme_code}"
    
    try:
        print(f"\n   🌐 Fetching: GET {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Check API status
        if data.get("status") != "SUCCESS":
            print(f"   ❌ API returned non-success status: {data.get('status')}")
            return None, None
        
        # Parse meta information
        meta = data.get("meta", {})
        print(f"   ✅ Response received!")
        print(f"      Fund House:    {meta.get('fund_house', 'N/A')}")
        print(f"      Scheme Name:   {meta.get('scheme_name', 'N/A')}")
        print(f"      Scheme Type:   {meta.get('scheme_type', 'N/A')}")
        print(f"      Category:      {meta.get('scheme_category', 'N/A')}")
        
        # Parse NAV data into DataFrame
        nav_records = data.get("data", [])
        if not nav_records:
            print(f"   ⚠️  No NAV records returned!")
            return meta, pd.DataFrame()
        
        df_nav = pd.DataFrame(nav_records)
        
        # Convert date format from DD-MM-YYYY to YYYY-MM-DD
        df_nav["date"] = pd.to_datetime(df_nav["date"], format="%d-%m-%Y", errors="coerce")
        df_nav["date"] = df_nav["date"].dt.strftime("%Y-%m-%d")
        
        # Convert NAV to float
        df_nav["nav"] = pd.to_numeric(df_nav["nav"], errors="coerce")
        
        # Add scheme code column
        df_nav["amfi_code"] = scheme_code
        
        # Sort by date ascending
        df_nav = df_nav.sort_values("date").reset_index(drop=True)
        
        # Reorder columns
        df_nav = df_nav[["amfi_code", "date", "nav"]]
        
        print(f"      Total Records: {len(df_nav):,}")
        print(f"      Date Range:    {df_nav['date'].iloc[0]} to {df_nav['date'].iloc[-1]}")
        print(f"      Latest NAV:    ₹{df_nav['nav'].iloc[-1]:.4f}")
        
        return meta, df_nav
        
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timed out for scheme {scheme_code}")
        return None, None
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error — check your internet connectivity")
        return None, None
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ HTTP error: {e}")
        return None, None
    except json.JSONDecodeError:
        print(f"   ❌ Failed to parse JSON response")
        return None, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return None, None


def save_individual_csv(df_nav, scheme_code, scheme_name):
    """Save NAV data for a single scheme as an individual CSV file."""
    filename = f"live_nav_{scheme_code}.csv"
    filepath = os.path.join(RAW_DATA_DIR, filename)
    df_nav.to_csv(filepath, index=False)
    print(f"   💾 Saved: {filepath} ({len(df_nav):,} rows)")
    return filepath


def save_combined_csv(all_navs):
    """Save combined NAV data for all schemes into a single CSV file."""
    filepath = os.path.join(RAW_DATA_DIR, "live_nav_all_schemes.csv")
    df_combined = pd.concat(all_navs, ignore_index=True)
    df_combined.to_csv(filepath, index=False)
    print(f"\n💾 Combined CSV saved: {filepath} ({len(df_combined):,} rows)")
    return df_combined


def main():
    """Main execution flow for live NAV fetching."""
    print("\n")
    print_header("BLUESTOCK FINTECH — DAY 1: LIVE NAV FETCHER")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  API Base URL: {MFAPI_BASE_URL}")
    print(f"  Schemes to fetch: {len(SCHEMES)}")
    print_separator()
    
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    all_navs = []
    all_metas = []
    success_count = 0
    fail_count = 0
    
    for scheme_code, scheme_name in SCHEMES.items():
        print(f"\n{'─' * 70}")
        print(f"📊 Scheme: {scheme_name}")
        print(f"   AMFI Code: {scheme_code}")
        
        meta, df_nav = fetch_nav_data(scheme_code)
        
        if df_nav is not None and len(df_nav) > 0:
            # Save individual CSV
            save_individual_csv(df_nav, scheme_code, scheme_name)
            all_navs.append(df_nav)
            all_metas.append(meta)
            success_count += 1
        else:
            fail_count += 1
            print(f"   ⚠️  Skipping scheme {scheme_code} — no data fetched")
    
    # Save combined CSV
    if all_navs:
        print(f"\n{'─' * 70}")
        print(f"📦 Combining all NAV data...")
        df_combined = save_combined_csv(all_navs)
        
        # Summary statistics
        print(f"\n{'─' * 70}")
        print(f"📊 Combined Data Summary:")
        print(f"   Shape: {df_combined.shape}")
        print(f"   Schemes: {df_combined['amfi_code'].nunique()}")
        print(f"   Date range: {df_combined['date'].min()} to {df_combined['date'].max()}")
        print(f"\n   Per-scheme record counts:")
        for code, count in df_combined.groupby("amfi_code").size().items():
            name = SCHEMES.get(code, "Unknown")
            print(f"      • {code} ({name[:40]}): {count:,} records")
    
    # Final summary
    print_header("LIVE NAV FETCH COMPLETE ✅")
    print(f"\n  ✅ Successful: {success_count}/{len(SCHEMES)}")
    if fail_count > 0:
        print(f"  ❌ Failed: {fail_count}/{len(SCHEMES)}")
    print(f"  📂 Files saved to: {os.path.abspath(RAW_DATA_DIR)}")
    print(f"  🕐 Completed at {datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == "__main__":
    main()
