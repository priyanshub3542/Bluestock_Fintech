# 📊 Bluestock Mutual Fund Analytics — Capstone Project

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-Data_Analysis-150458?logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-In_Progress-orange" />
</p>

> **Bluestock Fintech Pvt. Ltd.** | Data Analyst Internship  
> **Intern:** Priyanshu Bisht ([@priyanshub3542](https://github.com/priyanshub3542))  
> **Duration:** 45 Days

---

## 🎯 Project Overview

An end-to-end **Mutual Fund Analytics Pipeline** covering data ingestion, cleaning, SQL analysis, statistical modelling, and interactive dashboard creation using **10 real-world MF datasets** from the Indian mutual fund industry.

### What This Project Does

- 📥 **Ingests** 10 CSV datasets + live NAV data from [MFAPI](https://www.mfapi.in)
- 🧹 **Cleans & validates** all datasets with business rules
- 🗄️ **Loads** into a star-schema **SQLite database** (dim + fact tables)
- 📊 **Analyzes** with 10 analytical SQL queries
- 📖 **Documents** everything in a comprehensive data dictionary

---

## 📁 Project Structure

```
Bluestock_Fintech/
├── data/
│   ├── raw/                  # Original + live-fetched CSV datasets (10 + 7)
│   └── processed/            # Cleaned & validated datasets (10 CSVs)
├── notebooks/                # Jupyter notebooks (upcoming)
├── sql/
│   ├── schema.sql            # Star-schema DDL (2 dim + 6 fact + 3 tables)
│   └── queries.sql           # 10 analytical SQL queries
├── dashboard/                # Interactive dashboards (upcoming)
├── reports/
│   └── data_quality_summary.txt
├── data_ingestion.py         # Day 1: Load & explore all datasets
├── live_nav_fetch.py         # Day 1: Fetch live NAV from MFAPI
├── data_cleaning.py          # Day 2: Clean & validate all datasets
├── db_loader.py              # Day 2: Load into SQLite + verify
├── data_dictionary.md        # Day 2: Full column-level documentation
├── requirements.txt          # Python dependencies
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

**Total: 87,533 records across 10 datasets**

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
# Step 1: Load & explore raw data
python data_ingestion.py

# Step 2: Fetch live NAV from MFAPI
python live_nav_fetch.py

# Step 3: Clean all datasets
python data_cleaning.py

# Step 4: Build SQLite database + run queries
python db_loader.py
```

---

## 📊 Sample SQL Queries

The project includes **10 analytical queries** in [`sql/queries.sql`](sql/queries.sql):

| # | Query | Key Insight |
|---|-------|-------------|
| 1 | Top 5 Funds by AUM | Mirae Emerging Bluechip leads at ₹49,046 Cr |
| 2 | Avg NAV per Month (Large Cap) | 53 months of trend data |
| 3 | SIP Year-over-Year Growth | 15–26% YoY growth observed |
| 4 | Transactions by State | Maharashtra, Karnataka, Delhi top states |
| 5 | Funds with Expense Ratio < 1% | 14 cost-efficient funds identified |
| 6 | Category-wise Net Inflows | Liquid funds dominate inflows |
| 7 | Alpha Ranking (Top 10) | Best benchmark-beating funds |
| 8 | Monthly Transaction Trend | ~1,900 transactions/month average |
| 9 | Gender Demographics | Near-equal average investment sizes |
| 10 | Risk-Grade Sharpe Ratios | Low risk: 3.95 vs Very High: 0.86 |

---

## 📈 Day-wise Progress

- [x] **Day 1:** Data ingestion, live NAV fetch, data quality validation
- [x] **Day 2:** Data cleaning, SQLite DB, SQL queries, data dictionary
- [ ] **Day 3–5:** Statistical analysis & EDA
- [ ] **Day 6–10:** Advanced analytics & modelling
- [ ] **Day 11–20:** Dashboard development
- [ ] **Day 21–45:** Final report & presentation

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Core programming language |
| **Pandas / NumPy** | Data manipulation & analysis |
| **SQLAlchemy** | Database ORM & connection |
| **SQLite** | Lightweight relational database |
| **Matplotlib / Seaborn / Plotly** | Data visualization |
| **Requests** | API calls to MFAPI |
| **SciPy** | Statistical analysis |
| **Jupyter** | Interactive notebooks |

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
