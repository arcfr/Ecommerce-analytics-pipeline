import pandas as pd
import re
import os

def execute_cleaning_pipeline():
    raw_dir, clean_dir = "data/raw", "data/cleaned"
    os.makedirs(clean_dir, exist_ok=True)
    report = {}
    
    # 1. Clean Orders Table [cite: 41]
    orders_df = pd.read_csv(f"{raw_dir}/orders.csv")
    report["Total Raw Orders Scanned"] = len(orders_df)
    
    null_cust_mask = orders_df["customer_id"].isna() | (orders_df["customer_id"] == "")
    report["Anomalies Detected: Missing Customer IDs (Dropped)"] = int(null_cust_mask.sum())
    orders_df = orders_df[~null_cust_mask].copy()
    
    def parse_date(val):
        val = str(val).strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y"):
            try: return pd.to_datetime(val, format=fmt)
            except ValueError: continue
        return pd.NaT

    orders_df["order_date"] = orders_df["order_date"].apply(parse_date).dt.strftime("%Y-%m-%d %H:%M:%S")
    orders_df = orders_df.dropna(subset=["order_date"])
    orders_df.to_csv(f"{clean_dir}/orders.csv", index=False)
    
    # 2. Clean Products Table [cite: 42]
    products_df = pd.read_csv(f"{raw_dir}/products.csv")
    report["Total Raw Products Scanned"] = len(products_df)
    products_df["product_name"] = products_df["product_name"].astype(str).str.strip().str.title()
    products_df.to_csv(f"{clean_dir}/products.csv", index=False)
    
    # 3. Validate Customer Emails [cite: 43]
    customers_df = pd.read_csv(f"{raw_dir}/customers.csv")
    report["Total Raw Customers Scanned"] = len(customers_df)
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    invalid_mask = ~customers_df["email"].astype(str).str.match(email_regex, na=False)
    
    invalid_cust_ids = customers_df[invalid_mask]["customer_id"].tolist()
    report["Anomalies Detected: Malformed Emails Found"] = len(invalid_cust_ids)
    report["Flagged Invalid Email Customer IDs List"] = invalid_cust_ids
    customers_df.to_csv(f"{clean_dir}/customers.csv", index=False)
    
    # 4. Check Referential Integrity Boundaries [cite: 45]
    items_df = pd.read_csv(f"{raw_dir}/order_items.csv")
    report["Total Raw Order Items Scanned"] = len(items_df)
    report["Metrics: Negative Transaction Balances (Returns Tracked)"] = int((items_df["quantity"] < 0).sum())
    
    valid_order_ids = set(orders_df["order_id"])
    orphan_mask = ~items_df["order_id"].isin(valid_order_ids)
    orphan_order_ids = items_df[orphan_mask]["order_id"].unique().tolist()
    
    report["Anomalies Detected: Broken Referential Integrity Items (Dropped)"] = int(orphan_mask.sum())
    report["Flagged Orphan Order IDs List"] = orphan_order_ids
    
    cleaned_items = items_df[~orphan_mask].copy()
    cleaned_items.to_csv(f"{clean_dir}/order_items.csv", index=False)
    
    # Write the mandatory text report [cite: 46]
    report_path = f"{clean_dir}/integrity_report.txt"
    with open(report_path, "w") as f:
        f.write("Pipeline data report")
        for k, v in report.items():
            f.write(f"{k}: {v}\n")
            
    print(f" Cleaning execution finished. Logs saved to '{report_path}'.")

if __name__ == "__main__":
    execute_cleaning_pipeline()