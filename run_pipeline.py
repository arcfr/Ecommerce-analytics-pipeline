import os
import sqlite3
import pandas as pd

from src.generator import generate_raw_data
from src.cleaner import execute_cleaning_pipeline
from src.queries import SQL_QUERIES
from src.reports import run_cli
from tests.test_cases import run_test_suite

def build_database(db_path="database/analytics.db", clean_dir="data/cleaned"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    tables = ["products", "customers", "orders", "order_items"]
    for t in tables:
        df = pd.read_csv(f"{clean_dir}/{t}.csv")
        df.to_sql(t, conn, if_exists="replace", index=False)
        
    print(f"Clean staging records structuralized inside DB: '{db_path}'")
    conn.close()

def execute_analytical_queries(db_path="database/analytics.db"):
    conn = sqlite3.connect(db_path)
    print("\nRunning analytical queries")
    
    # Demonstrate key advanced analytical blocks
    sample_queries = ["revenue_per_category", "top_10_customers", "category_return_rate", "yoy_revenue_comparison"]
    
    for q_key in sample_queries:
        print(f"\n[QUERY TARGET]: {q_key.replace('_',' ').upper()}")
        df = pd.read_sql_query(SQL_QUERIES[q_key], conn)
        print(df.head(5).to_string(index=False))
        
    conn.close()

if __name__ == "__main__":
    # Step 1: Synthesize Raw Records with anomalies
    generate_raw_data()
    
    # Step 2: Clean and log data issues
    execute_cleaning_pipeline()
    
    # Step 3: Seed Database Engine
    build_database()
    
    # Step 4: Execute advanced SQL analytics 
    execute_analytical_queries()
    
    # Step 5: Run Edge Case Test Suite
    print("\nRun edge case")
    run_test_suite()
    
    # Step 6: Initialize Interactive CLI Reporting App
    print("\n")
    run_cli()