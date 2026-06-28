import sqlite3
from datetime import datetime, timedelta

def get_period_dates(report_type, end_date_str):
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    if report_type == "daily":
        start_date = end_date
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end
    elif report_type == "weekly":
        start_date = end_date - timedelta(days=6)
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=6)
    elif report_type == "monthly":
        start_date = end_date - timedelta(days=29)
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=29)
    else:
        raise ValueError("Unsupported operational mode.")
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), prev_start.strftime("%Y-%m-%d"), prev_end.strftime("%Y-%m-%d")

def generate_summary(db_path, r_type, target_date):
    s1, e1, s2, e2 = get_period_dates(r_type, target_date)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    def fetch_metrics(start, end):
        q = f"""
            SELECT COUNT(DISTINCT o.order_id),
                   COALESCE(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)), 0),
                   COUNT(DISTINCT o.customer_id)
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE date(o.order_date) BETWEEN '{start}' AND '{end}'
        """
        cur.execute(q)
        return cur.fetchone()

    o1, r1, c1 = fetch_metrics(s1, e1)
    o2, r2, c2 = fetch_metrics(s2, e2)
    
    chg_o = ((o1 - o2) / o2 * 100) if o2 > 0 else 0.0
    chg_r = ((r1 - r2) / r2 * 100) if r2 > 0 else 0.0
    
    top_p_q = f"""
        SELECT p.product_name, SUM(oi.quantity) as volume
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE date(o.order_date) BETWEEN '{s1}' AND '{e1}'
        GROUP BY p.product_name ORDER BY volume DESC LIMIT 3
    """
    cur.execute(top_p_q)
    top_products = cur.fetchall()
    conn.close()
    
    print("\n" + "="*55)
    print(f"      E-COMMERCE OPERATIONAL CONSOLE REPORT ({r_type.upper()})")
    print(f"      Target Window  : {s1} to {e1}")
    print(f"      Prior Baseline : {s2} to {e2}")
    print("="*55)
    print(f" Total Completed Orders   : {o1} ({chg_o:+.1f}% vs baseline)")
    print(f" Gross Realized Revenue   : ${r1:,.2f} ({chg_r:+.1f}% vs baseline)")
    print(f" Active Unique Customers  : {c1}")
    print("-"*55)
    print(" TOP VELOCITY PRODUCT VARIETIES:")
    for idx, (name, vol) in enumerate(top_products, 1):
        print(f"  {idx}. {name} (Volume Handled: {vol})")
    print("="*55 + "\n")

def run_cli(db_path="database/analytics.db"):
    print("--- Executive Management Query Engine ---")
    rtype = input("Select report cycle type (daily/weekly/monthly): ").strip().lower()
    tdate = input("Enter execution date parameter (YYYY-MM-DD): ").strip()
    try:
        generate_summary(db_path, rtype, tdate)
    except Exception as e:
        print(f"[CLI ABORT] Operational processing failure: {e}")

if __name__ == "__main__":
    run_cli()