import os
import sqlite3
import pandas as pd

def seed_relational_database(db_path="database/analytics.db", clean_dir="data/cleaned"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    print(f"Initializing structural injection into target database: '{db_path}'...")
    
    tables = ["products", "customers", "orders", "order_items"]
    for table in tables:
        path = f"{clean_dir}/{table}.csv"
        if not os.path.exists(path):
            print(f"[FATAL] Staging source data block missing: {path}")
            return
        df = pd.read_csv(path)
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f" * Instantiated and seeded table [{table}] with {len(df)} production records.")
        
    conn.close()
    print("Relational seed operations finished successfully.")

if __name__ == "__main__":
    seed_relational_database()