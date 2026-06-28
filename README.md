# E-Commerce Order Analytics System

An end-to-end data engineering pipeline built using Python and SQLite. The system handles synthetic data generation (with intentional anomalies), automated data cleansing, database ingestion, advanced analytical SQL querying, and an interactive command-line operational dashboard.

---

## Project Structure & File Directory

```text
ecommerce_analytics/
│
├── data/
│   ├── raw/                  # Dirty data generated with intentional errors
│   └── cleaned/              # Cleaned CSV datasets + validation anomaly log
│
├── database/
│   |── analytics.db          # Self-contained SQLite database file 
|   |── analysis_queries.sql  # SQL script file containing your 16 analytical queries (SQLTools ready)
│
├── src/
│   ├── __init__.py           # Declares 'src' folder as a Python package module
│   ├── generator.py          # Part 1: Synthesizes messy raw CSV records (>= 500 rows each)
│   ├── cleaner.py            # Part 2: Cleans dates, trims strings, checks foreign keys
│   ├── queries.py            # Portfolio module holding all 16 analytical SQL blocks in a dictionary
│   └── reports.py            # Part 4: Interactive, pure-Python CLI summary engine
│
├── tests/
│   └── test_cases.py    # Part 5: Automated guardrail unit tests (catches out-of-bound errors)
│
├── database_pipeline.py      # Automated ETL script that seeds clean CSV records into tables
├── run_pipeline.py           # The Master script that orchestrates the entire system end-to-end
├   
└── run_queries.py            # Utility script to test any of the 16 SQL queries inside the terminal

By 
Archit Sahay