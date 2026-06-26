# 📊 Bluestock Mutual Fund Analytics — Capstone Project

> **Bluestock Fintech Pvt. Ltd.** | Data Analyst Internship  
> **Intern:** Data Analyst Intern  
> **Duration:** 45 Days (Day 1 – Day 45)

---

## 🎯 Project Overview

End-to-end Mutual Fund analytics pipeline covering data ingestion, cleaning, SQL analysis, statistical modelling, and interactive dashboard creation using **10 real-world MF datasets** from the Indian mutual fund industry.

## 📁 Project Structure

```
Bluestock_MF_Datasets/
├── data/
│   ├── raw/              # Original + live-fetched CSV datasets
│   └── processed/        # Cleaned & transformed datasets
├── notebooks/            # Jupyter notebooks for EDA & analysis
├── sql/                  # SQL scripts for database queries
├── dashboard/            # Interactive dashboard files
├── reports/              # Generated reports & summaries
├── data_ingestion.py     # Day 1: Data loading & exploration
├── live_nav_fetch.py     # Day 1: Live NAV fetcher from MFAPI
├── requirements.txt      # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 📦 Datasets

| # | File | Description | Records |
|---|------|-------------|---------|
| 1 | `01_fund_master.csv` | Scheme metadata (fund house, category, risk, expense ratio) | 41 |
| 2 | `02_nav_history.csv` | Daily NAV history for all schemes (2022–2025) | 46,001 |
| 3 | `03_aum_by_fund_house.csv` | AUM trends by fund house (quarterly) | 91 |
| 4 | `04_monthly_sip_inflows.csv` | Monthly SIP inflow & account data | 49 |
| 5 | `05_category_inflows.csv` | Category-wise net inflows | 145 |
| 6 | `06_industry_folio_count.csv` | Industry folio count growth | 22 |
| 7 | `07_scheme_performance.csv` | Returns, alpha, beta, Sharpe ratios | 41 |
| 8 | `08_investor_transactions.csv` | Individual investor transactions | 32,779 |
| 9 | `09_portfolio_holdings.csv` | Stock-level portfolio holdings | 323 |
| 10 | `10_benchmark_indices.csv` | Benchmark index daily close values | 8,051 |

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-github-url>
cd Bluestock_MF_Datasets
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Day 1 Scripts
```bash
python data_ingestion.py      # Load & explore all datasets
python live_nav_fetch.py      # Fetch live NAV from MFAPI
```

## 📈 Day-wise Progress

- [x] **Day 1:** Data ingestion, live NAV fetch, data quality validation
- [ ] **Day 2–5:** Data cleaning & preprocessing
- [ ] **Day 6–10:** SQL database & queries
- [ ] **Day 11–15:** Statistical analysis
- [ ] **Day 16–20:** Advanced analytics
- [ ] **Day 21–30:** Dashboard development
- [ ] **Day 31–45:** Final report & presentation

## 🔗 Data Source

- **MFAPI:** [https://www.mfapi.in](https://www.mfapi.in) — Free Indian Mutual Fund NAV API
- **AMFI:** Association of Mutual Funds in India

## 📄 License

This project is part of the Bluestock Fintech internship program.
