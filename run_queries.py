import sqlite3
import pandas as pd
from src.queries import SQL_QUERIES

# Connect to your database
conn = sqlite3.connect("database/analytics.db")

# CHOOSE YOUR QUERY HERE:
# Options: revenue_per_category, top_10_customers, product_dense_rank,
#          customer_churn_gap, yoy_revenue_comparison, cohort_retention_matrix, etc.
QUERY_NAME = "revenue_per_category" 

print(f"\n--- Running: {QUERY_NAME.upper()} ---")
df = pd.read_sql_query(SQL_QUERIES[QUERY_NAME], conn)
print(df.to_string(index=False))

conn.close()