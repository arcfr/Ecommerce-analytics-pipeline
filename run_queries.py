import sqlite3
import pandas as pd
from src.queries import SQL_QUERIES

# Connect to your database
conn = sqlite3.connect("database/analytics.db")

# run query by altering the variable
QUERY_NAME = "revenue_per_category" 

print(f"\nRunning: {QUERY_NAME.upper()}")
df = pd.read_sql_query(SQL_QUERIES[QUERY_NAME], conn)
print(df.to_string(index=False))

conn.close()