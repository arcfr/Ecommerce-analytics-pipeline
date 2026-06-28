-- =====================================================================
-- PART 3: E-COMMERCE OPERATIONAL & ADVANCED SQL ANALYSIS
-- ENVIRONMENT: SQLite / VS Code SQLTools Compatible
-- =====================================================================

-- @block 1. Total revenue per category
-- Metric Rule: revenue = quantity * unit_price * (1 - discount_percent/100)
SELECT p.category,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;


-- @block 2. Top 10 customers by total order value
SELECT o.customer_id, c.customer_name,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.customer_id, c.customer_name
ORDER BY total_order_value DESC
LIMIT 10;


-- @block 3. Month-wise order count for the last 12 months
-- Dynamic subquery keeps this evaluation relative to the maximum calendar envelope in data
SELECT strftime('%Y-%m', order_date) AS order_month, 
       COUNT(order_id) AS order_count
FROM orders
WHERE order_date >= (SELECT date(MAX(order_date), '-12 months') FROM orders)
GROUP BY order_month
ORDER BY order_month ASC;


-- @block 4. Find customers who placed orders but never had any item delivered
SELECT DISTINCT o.customer_id, c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.customer_id NOT IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE status = 'DELIVERED' -- Filters out any customer who has achieved a delivery
);


-- @block 5. Products that were ordered but had more returns than purchases
-- Negative quantities directly signal return inventory movements
SELECT oi.product_id, p.product_name,
       SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS total_returned,
       SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS total_purchased
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.product_id, p.product_name
HAVING total_returned > total_purchased;


-- @block 6. Calculate the return rate per category
-- Return Rate Formula: returned items / total items
SELECT p.category,
       ROUND(CAST(SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS REAL) / 
             NULLIF(SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END), 0), 4) AS return_rate
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category;


-- @block 7. Running Totals with Window Functions
-- Required Outputs: region_code, order_date, daily revenue, running total
WITH daily_region_rev AS (
    SELECT o.region_code, date(o.order_date) AS order_date,
           SUM