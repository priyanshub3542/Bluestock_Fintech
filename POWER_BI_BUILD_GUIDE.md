# 📈 Bluestock Mutual Fund Dashboard — Power BI Build Guide

This guide provides step-by-step instructions and the exact DAX formulas you need to recreate the `bluestock_mf_dashboard.pbix` file using the cleaned data we generated.

## Phase 1: Data Connection & Relationships
1. Open Power BI Desktop.
2. Click **Get Data** -> **More** -> **ODBC**.
3. Select your SQLite ODBC driver DSN (if configured), OR simply import the 8 cleaned `.csv` files from `data/processed/`.
4. Go to the **Model View** and establish the following relationships:
   - `02_nav_history (amfi_code)` -> `01_fund_master (amfi_code)` [Many-to-One]
   - `07_scheme_performance (amfi_code)` -> `01_fund_master (amfi_code)` [One-to-One]
   - `08_investor_transactions (amfi_code)` -> `01_fund_master (amfi_code)` [Many-to-One]
   - Create a Master Date Table and link it to the `date` columns in all fact tables (NAV, Transactions, AUM, SIP).

## Phase 2: Create Measures (DAX)
Click **New Measure** to create the following:

```dax
Total AUM (Lakh Cr) = SUM('03_aum_by_fund_house'[aum_lakh_crore])
```

```dax
Total SIP Inflows (Cr) = SUM('04_monthly_sip_inflows'[sip_inflow_crore])
```

```dax
Total Folios = SUM('06_industry_folio_count'[total_folios_crore])
```

```dax
Total Schemes = DISTINCTCOUNT('01_fund_master'[amfi_code])
```

```dax
Transaction Volume = COUNTROWS('08_investor_transactions')
```

## Phase 3: Building the Pages

### Page 1 — Industry Overview
1. Add 4 **Card** visuals for the 4 DAX Measures created above.
2. **Line Chart**:
   - X-axis: Date (Quarter/Month)
   - Y-axis: `Total AUM (Lakh Cr)`
3. **Bar Chart**:
   - X-axis: `fund_house` (from `01_fund_master`)
   - Y-axis: `Total AUM (Lakh Cr)`

### Page 2 — Fund Performance
1. **Scatter Plot**:
   - X-axis: `mean_return_ann` (from `fund_scorecard.csv`)
   - Y-axis: `std_ann`
   - Values: `scheme_name`
   - Size: `aum_crore`
2. **Table**:
   - Add columns: `overall_rank`, `scheme_name`, `composite_score`, `cagr_3yr`, `sharpe_ratio`, `alpha_annual_pct` from the scorecard.
3. **Line Chart (NAV)**:
   - X-axis: `date`
   - Y-axis: `nav`
   - Legend: `scheme_name`
4. Add **Slicers** for `fund_house`, `category`, and `plan`.

### Page 3 — Investor Analytics
1. **Clustered Bar Chart**:
   - Y-axis: `state`
   - X-axis: `amount_inr`
2. **Donut Chart**:
   - Legend: `transaction_type`
   - Values: `amount_inr`
3. **Column Chart**:
   - X-axis: `age_group`
   - Y-axis: Average of `amount_inr` (Filter: `transaction_type = "SIP"`)
4. Add **Slicers** for `state`, `age_group`, and `city_tier`.

### Page 4 — SIP & Market Trends
1. **Line and Clustered Column Chart (Dual-Axis)**:
   - X-axis: `month`
   - Column Y-axis: `sip_inflow_crore`
   - Line Y-axis: `close_value` (NIFTY 50)
2. **Matrix (Heatmap)**:
   - Rows: `category`
   - Columns: `month`
   - Values: `net_inflow_crore` (Apply Conditional Formatting -> Background Color)
3. **Bar Chart**:
   - Filter to FY25 dates
   - X-axis: `category`
   - Y-axis: `net_inflow_crore` (Top 5)

## Phase 4: Finalizing
- Apply the **Bluestock colour theme** (`#1a73e8`, `#34a853`, `#ea4335`, `#fbbc04`).
- Setup Drill-through: Right-click the Fund Performance table, add a drill-through field (`amfi_code`) to jump to a hidden NAV details page.
- Export your final result to `.pbix` and `.pdf`!
