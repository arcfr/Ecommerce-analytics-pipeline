import csv
import random
import os
from datetime import datetime, timedelta

def generate_raw_data(output_dir="data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)
    
    # 1. Generate Products (Ensuring AT LEAST 500 rows as requested)
    categories = {
        "Electronics": ["Smart Watch", "Laptop", "Wireless Earbuds", "Bluetooth Speaker", "Tablet", "Monitor"],
        "Clothing": ["Denim Jacket", "Running Shoes", "Hoodie", "Cotton T-Shirt", "Socks", "Sweater"],
        "Home": ["Desk Lamp", "Air Purifier", "Coffee Maker", "Blender", "Toaster", "Vacuum"],
        "Books": ["Sci-Fi Novel", "Python Guide", "History Anthology", "Biographies", "Fiction", "Comic"]
    }
    
    products = []
    for i in range(1, 520):  # Over 500 rows
        cat = random.choice(list(categories.keys()))
        subcat = random.choice(categories[cat])
        p_name = f"{subcat} Model-{i}"
        
        # Inject messy names (extra spaces or mixed case)
        if random.random() < 0.15:
            p_name = f"  {p_name.lower()}   " if i % 2 == 0 else f"mIxEd {p_name.upper()}"
            
        products.append({
            "product_id": f"P{i:03d}",
            "product_name": p_name,
            "category": cat,
            "subcategory": subcat,
            "cost_price": round(random.uniform(10.0, 500.0), 2)
        })
        
    with open(f"{output_dir}/products.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category", "subcategory", "cost_price"])
        w.writeheader()
        w.writerows(products)

    # 2. Generate Customers (At least 500 rows)
    first_names = ["John", "Jane", "Alex", "Emily", "Michael", "Sarah", "David", "Jessica", "Archit", "Swayam"]
    last_names = ["Smith", "Doe", "Jones", "Brown", "Miller", "Davis", "Garcia", "Sahay", "Kohli", "Singh"]
    customer_types = ["REGULAR", "PREMIUM", "VIP"]
    
    customers = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(1, 550):
        c_id = f"C{i:03d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{name.lower().replace(' ', '')}@example.com"
        
        # Inject invalid emails (2%)
        if random.random() < 0.02:
            email = email.replace("@", "") if i % 2 == 0 else email.split(".")[0]
            
        reg_days = random.randint(0, 400)
        reg_date = (base_date + timedelta(days=reg_days)).strftime("%Y-%m-%d")
        
        customers.append({
            "customer_id": c_id,
            "customer_name": name,
            "email": email,
            "registration_date": reg_date,
            "customer_type": random.choice(customer_types)
        })
        
    with open(f"{output_dir}/customers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["customer_id", "customer_name", "email", "registration_date", "customer_type"])
        w.writeheader()
        w.writerows(customers)

    # 3. Generate Orders (At least 500 rows)
    orders = []
    regions = ["US", "EU", "APAC", "IN"]
    statuses = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
    start_order_date = datetime(2024, 6, 1)
    
    for i in range(1, 600):
        o_id = f"O{i:04d}"
        
        # Inject NULL customer IDs (5%)
        c_id = "" if random.random() < 0.05 else f"C{random.randint(1, 549)}"
        
        o_days = random.randint(0, 700)
        o_date_obj = start_order_date + timedelta(days=o_days)
        
        # Inject malformed dates (DD-MM-YYYY)
        if random.random() < 0.08:
            o_date = o_date_obj.strftime("%d-%m-%Y")
        else:
            o_date = o_date_obj.strftime("%Y-%m-%d %H:%M:%S")
            
        orders.append({
            "order_id": o_id,
            "customer_id": c_id,
            "order_date": o_date,
            "status": random.choice(statuses),
            "region_code": random.choice(regions)
        })
        
    with open(f"{output_dir}/orders.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["order_id", "customer_id", "order_date", "status", "region_code"])
        w.writeheader()
        w.writerows(orders)

    # 4. Generate Order Items (At least 500 rows)
    order_items = []
    item_id_counter = 1
    
    for o in orders:
        items_count = random.randint(1, 3)
        for _ in range(items_count):
            p = random.choice(products)
            qty = random.randint(1, 5)
            
            # Inject negative quantities (3%)
            if random.random() < 0.03:
                qty = -qty
                
            u_price = round(p["cost_price"] * random.uniform(1.2, 1.5), 2)
            disc = random.choice([0, 5, 10, 15, 20])
            
            order_items.append({
                "item_id": f"I{item_id_counter:05d}",
                "order_id": o["order_id"],
                "product_id": p["product_id"],
                "quantity": qty,
                "unit_price": u_price,
                "discount_percent": disc
            })
            item_id_counter += 1
            
    # Inject 5 orphan order items to test check_referential_integrity()
    for k in range(5):
        p = random.choice(products)
        order_items.append({
            "item_id": f"I{item_id_counter:05d}",
            "order_id": f"O999{k}", 
            "product_id": p["product_id"],
            "quantity": random.randint(1, 3),
            "unit_price": 45.0,
            "discount_percent": 0
        })
        item_id_counter += 1

    with open(f"{output_dir}/order_items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])
        w.writeheader()
        w.writerows(order_items)
        
    print("[SUCCESS] All 4 files generated with 500+ records and distinct anomalies.")
if __name__ == "__main__":
    print("Starting data generation pipeline...")
    generate_raw_data()    