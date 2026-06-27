# 📊 Bluestock Mutual Fund Analytics — Capstone Project

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-Data_Analysis-150458?logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/Plotly-Interactive_Charts-3F4F75?logo=plotly&logoColor=white" />
  <img src="https://img.shields.io/badge/Seaborn-Visualisation-76B7B2" />
  <img src="https://img.shields.io/badge/Status-Day_3_Complete-brightgreen" />
</p>

> **Bluestock Fintech Pvt. Ltd.** | Data Analyst Internship  
> **Intern:** Priyanshu Bisht ([@priyanshub3542](https://github.com/priyanshub3542))  
> **Duration:** 45 Days

---

## 🎯 Project Overview

An end-to-end **Mutual Fund Analytics Pipeline** covering data ingestion, cleaning, SQL analysis, exploratory data analysis, and interactive dashboard creation using **10 real-world MF datasets** from the Indian mutual fund industry.

### What This Project Does

- 📥 **Ingests** 10 CSV datasets + live NAV data from [MFAPI](https://www.mfapi.in) (Day 1)
- 🧹 **Cleans & validates** all datasets with business rules (Day 2)
- 🗄️ **Loads** into a star-schema **SQLite database** with 11 tables (Day 2)
- 📊 **Analyses** with 10 analytical SQL queries (Day 2)
- 📈 **Visualises** with 15+ charts using Plotly, Seaborn & Matplotlib (Day 3)
- 📖 **Documents** everything in a comprehensive data dictionary (Day 2)

---

## 📁 Project Structure

```
Bluestock_Fintech/
│
├── data/
│   ├── raw/                          # 10 original + 7 live-fetched CSVs
│   │   ├── 01_fund_master.csv        # 40 schemes
│   │   ├── 02_nav_history.csv        # 46,000 daily NAV records
│   │   ├── 03_aum_by_fund_house.csv  # 90 quarterly AUM records
│   │   ├── 04_monthly_sip_inflows.csv
│   │   ├── 05_category_inflows.csv
│   │   ├── 06_industry_folio_count.csv
│   │   ├── 07_scheme_performance.csv
│   │   ├── 08_investor_transactions.csv  # 32,778 transactions
│   │   ├── 09_portfolio_holdings.csv
│   │   ├── 10_benchmark_indices.csv      # 8,050 index records
│   │   └── live_nav_*.csv                # 7 live-fetched NAV files
│   │
│   └── processed/                    # 10 cleaned & validated CSVs
│
├── sql/
│   ├── schema.sql                    # Star-schema DDL (11 tables)
│   └── queries.sql                   # 10 analytical SQL queries
│
├── reports/
│   ├── charts/                       # 15+ exported charts (PNG + HTML)
│   │   ├── 01_nav_trends.png
│   │   ├── 02_aum_growth.png
│   │   ├── 03_sip_inflow.html        # Interactive Plotly
│   │   ├── 04_category_heatmap.png
│   │   ├── 05_age_pie.png
│   │   ├── 06_sip_boxplot.png
│   │   ├── 07_gender_split.png
│   │   ├── 08_geographic_state.png
│   │   ├── 09_city_tier.png
│   │   ├── 10_folio_growth.html      # Interactive Plotly
│   │   ├── 11_correlation_matrix.png
│   │   ├── 12_sector_donut.png
│   │   ├── 13_expense_vs_return.png
│   │   ├── 14_txn_volume.png
│   │   └── 15_morningstar.png
│   └── data_quality_summary.txt
│
├── notebooks/                        # Jupyter notebooks
├── dashboard/                        # Interactive dashboards (upcoming)
│
├── data_ingestion.py                 # Day 1: Load & explore all datasets
├── live_nav_fetch.py                 # Day 1: Fetch live NAV from MFAPI
├── data_cleaning.py                  # Day 2: Clean & validate all datasets
├── db_loader.py                      # Day 2: Load into SQLite + verify
├── eda_analysis.py                   # Day 3: Generate 15 charts as PNGs
├── generate_notebook.py              # Day 3: Build EDA_Analysis.ipynb
├── EDA_Analysis.ipynb                # Day 3: Jupyter notebook (29 cells)
│
├── data_dictionary.md                # Full column-level documentation
├── requirements.txt                  # Python dependencies
├── .gitignore
└── README.md
```

---

## 📦 Datasets

| # | File | Description | Records |
|---|------|-------------|---------|
| 1 | `01_fund_master.csv` | Scheme metadata — fund house, category, risk, expense ratio | 40 |
| 2 | `02_nav_history.csv` | Daily NAV history for all schemes (2022–2026) | 46,000 |
| 3 | `03_aum_by_fund_house.csv` | AUM trends by fund house (quarterly) | 90 |
| 4 | `04_monthly_sip_inflows.csv` | Monthly SIP inflow & account data | 48 |
| 5 | `05_category_inflows.csv` | Category-wise net inflows | 144 |
| 6 | `06_industry_folio_count.csv` | Industry folio count growth | 21 |
| 7 | `07_scheme_performance.csv` | Returns, alpha, beta, Sharpe ratios | 40 |
| 8 | `08_investor_transactions.csv` | Individual investor transactions | 32,778 |
| 9 | `09_portfolio_holdings.csv` | Stock-level portfolio holdings | 322 |
| 10 | `10_benchmark_indices.csv` | Benchmark index daily close values | 8,050 |

**Total: 87,533 records across 10 datasets + 19,906 live NAV records**

---

## 🗄️ Database Schema

Star schema with **11 tables** in SQLite:

| Table | Type | Rows | Description |
|-------|------|------|-------------|
| `dim_fund` | Dimension | 40 | Fund/scheme master data |
| `dim_date` | Dimension | 10,227 | Calendar dimension (2000–2027) |
| `fact_nav` | Fact | 46,000 | Daily NAV values |
| `fact_transactions` | Fact | 32,778 | Investor transactions |
| `fact_performance` | Fact | 40 | Scheme performance metrics |
| `fact_aum` | Fact | 90 | AUM by fund house |
| `fact_sip_inflows` | Fact | 48 | Monthly SIP data |
| `fact_category_inflows` | Fact | 144 | Category-wise inflows |
| `portfolio_holdings` | Table | 322 | Stock-level holdings |
| `benchmark_indices` | Table | 8,050 | Benchmark daily closes |
| `industry_folio_count` | Table | 21 | Folio count trends |

**Total: 97,760 rows | Database size: 8.93 MB**

---

## 📈 EDA Charts (Day 3)

15 publication-quality charts generated using **Plotly**, **Seaborn**, and **Matplotlib**:

| # | Chart | Library | Key Finding |
|---|-------|---------|-------------|
| 1 | NAV Trends (40 schemes) | Plotly | 2023 bull run + 2024 correction visible |
| 2 | AUM Growth by Fund House | Seaborn | SBI dominates at ₹12.5 Lakh Crore |
| 3 | SIP Inflow Time-Series | Plotly | ₹31,002 Cr all-time high (Dec 2025) |
| 4 | Category Inflow Heatmap | Seaborn | Liquid funds show highest volatility |
| 5 | Age Group Pie Chart | Matplotlib | 26-35 age group dominates investing |
| 6 | SIP Box Plot by Age | Seaborn | Median SIP amounts by age cohort |
| 7 | Gender Split | Seaborn | Near-parity in investment ticket sizes |
| 8 | Top 15 States Bar Chart | Seaborn | Top 3 states highlighted in red |
| 9 | T30 vs B30 City Tier Pie | Matplotlib | T30 metro cities account for 60%+ |
| 10 | Folio Count Growth | Plotly | 13.26 Cr → 26+ Cr with milestones |
| 11 | Correlation Matrix | Seaborn | Equity funds 0.85+ correlated |
| 12 | Sector Allocation Donut | Matplotlib | Banking (19.2%) & IT (13.4%) lead |
| 13 | Expense Ratio vs Return | Seaborn | Bubble scatter (size = AUM) |
| 14 | Transaction Volume Stacked | Matplotlib | SIP dominates monthly volume |
| 15 | Morningstar Rating | Seaborn | Higher rating → higher returns |

### 🔑 10 Key EDA Findings

| # | Finding |
|---|---------|
| 1 | All equity funds show a clear 2023 bull run followed by 2024 market corrections |
| 2 | SBI Mutual Fund's AUM grew from ₹6L Cr to ₹12.5L Cr, maintaining #1 position |
| 3 | Monthly SIP inflows nearly tripled from ₹11,500 Cr to ₹31,000+ Cr |
| 4 | Liquid funds exhibit the most volatile category inflows month-to-month |
| 5 | The 26-35 age group is the largest investor segment, driving MF growth via SIPs |
| 6 | Female investors show comparable average ticket sizes despite lower transaction frequency |
| 7 | T30 metro cities account for 60%+ of all transactions by value |
| 8 | Total MF folios nearly doubled from 13.26 Cr to 26+ Cr in 4 years |
| 9 | Large-cap equity funds are highly correlated (0.85+); debt offers diversification |
| 10 | Banking (19.2%) and IT (13.4%) sectors dominate equity portfolio allocation |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/priyanshub3542/Bluestock_Fintech.git
cd Bluestock_Fintech
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Pipeline
```bash
# Day 1: Load & explore raw data + fetch live NAV
python data_ingestion.py
python live_nav_fetch.py

# Day 2: Clean datasets + build SQLite database
python data_cleaning.py
python db_loader.py

# Day 3: Generate 15+ EDA charts as PNGs
python eda_analysis.py

# Day 3: Create Jupyter notebook
python generate_notebook.py
```

---

## 📊 Sample SQL Queries

The project includes **10 analytical queries** in [`sql/queries.sql`](sql/queries.sql):

| # | Query | Key Insight |
|---|-------|-------------|
| 1 | Top 5 Funds by AUM | Mirae Emerging Bluechip leads at ₹49,046 Cr |
| 2 | Avg NAV per Month (Large Cap) | 53 months of trend data |
| 3 | SIP Year-over-Year Growth | 15–26% YoY growth observed |
| 4 | Transactions by State | Top 10 states by investment volume |
| 5 | Funds with Expense Ratio < 1% | 14 cost-efficient funds identified |
| 6 | Category-wise Net Inflows | Liquid funds dominate inflows |
| 7 | Alpha Ranking (Top 10) | Best benchmark-beating funds |
| 8 | Monthly Transaction Trend | ~1,900 transactions/month average |
| 9 | Gender Demographics | Near-equal average investment sizes |
| 10 | Risk-Grade Sharpe Ratios | Low risk: 3.95 vs Very High: 0.86 |

---

## 📅 Day-wise Progress

| Day | Tasks | Status |
|-----|-------|--------|
| **Day 1** | Data ingestion, live NAV fetch, data quality validation | ✅ Complete |
| **Day 2** | Data cleaning, SQLite star-schema, SQL queries, data dictionary | ✅ Complete |
| **Day 3** | EDA with 15+ charts, Jupyter notebook, 10 key findings | ✅ Complete |
| Day 4–5 | Statistical analysis & hypothesis testing | ⬜ Upcoming |
| Day 6–10 | Advanced analytics & modelling | ⬜ Upcoming |
| Day 11–20 | Dashboard development | ⬜ Upcoming |
| Day 21–45 | Final report & presentation | ⬜ Upcoming |

### Git Commit History
```
0fbee2f  Day 3: EDA complete with 15+ charts
2bb566b  Cleanup: Remove duplicate root CSVs, PDF and DB binary
b65e1a1  Day 2: Cleaned data + SQLite DB loaded
732b34f  Day 1: Data ingestion complete
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Core programming language |
| **Pandas / NumPy** | Data manipulation & analysis |
| **SQLAlchemy** | Database ORM & SQLite connection |
| **SQLite** | Lightweight relational database |
| **Plotly** | Interactive charts (NAV trends, SIP, Folio growth) |
| **Seaborn** | Statistical visualisations (heatmaps, bar charts) |
| **Matplotlib** | Pie charts, donut charts, area charts |
| **Requests** | API calls to MFAPI |
| **SciPy** | Statistical analysis |
| **Jupyter / nbformat** | Notebook creation |
| **Kaleido** | Plotly chart export to PNG |

---

## 📂 Key Documentation

| Document | Description |
|----------|-------------|
| [`data_dictionary.md`](data_dictionary.md) | Full column-level documentation for all 11 tables |
| [`sql/schema.sql`](sql/schema.sql) | Star-schema DDL with indexes |
| [`sql/queries.sql`](sql/queries.sql) | 10 analytical SQL queries |
| [`EDA_Analysis.ipynb`](EDA_Analysis.ipynb) | Jupyter notebook with 15+ charts & findings |
| [`reports/data_quality_summary.txt`](reports/data_quality_summary.txt) | Day 1 data quality report |

---

## 🔗 Data Sources

- **MFAPI:** [https://www.mfapi.in](https://www.mfapi.in) — Free Indian Mutual Fund NAV API
- **AMFI:** Association of Mutual Funds in India

---

## 📄 License

This project is part of the **Bluestock Fintech** internship program.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/priyanshub3542">Priyanshu Bisht</a> | Bluestock Fintech Intern
</p>
