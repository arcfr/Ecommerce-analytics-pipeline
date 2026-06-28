

-- @block 1. Total revenue per category
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
    WHERE status = 'DELIVERED'
);


-- @block 5. Products that were ordered but had more returns than purchases
SELECT oi.product_id, p.product_name,
       SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS total_returned,
       SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS total_purchased
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.product_id, p.product_name
HAVING total_returned > total_purchased;


-- @block 6. Calculate the return rate per category
SELECT p.category,
       ROUND(CAST(SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS REAL) / 
             NULLIF(SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END), 0), 4) AS return_rate
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category;


-- @block 7. Running Totals with Window Functions
WITH daily_region_rev AS (
    SELECT o.region_code, 
           date(o.order_date) AS order_date,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.region_code, date(o.order_date)
)
SELECT region_code, 
       order_date, 
       ROUND(daily_revenue, 2) AS "daily revenue",
       ROUND(SUM(daily_revenue) OVER (PARTITION BY region_code ORDER BY order_date), 2) AS "running total"
FROM daily_region_rev
ORDER BY region_code, order_date;


-- @block 8. Ranking with DENSE_RANK
WITH product_revenues AS (
    SELECT p.category, 
           p.product_name,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_name
)
SELECT category, 
       product_name AS "product name", 
       ROUND(total_revenue, 2) AS "total revenue",
       DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS "rank in category"
FROM product_revenues;


-- @block 9. LAG/LEAD Analysis
WITH ordered_gaps AS (
    SELECT customer_id, 
           order_date,
           LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
    FROM orders
),
calculated_gaps AS (
    SELECT customer_id, 
           order_date, 
           previous_order_date,
           julianday(order_date) - julianday(previous_order_date) AS days_gap
    FROM ordered_gaps
    WHERE previous_order_date IS NOT NULL
)
SELECT customer_id, 
       order_date, 
       previous_order_date, 
       ROUND(days_gap, 1) AS days_gap,
       CASE WHEN AVG(days_gap) OVER (PARTITION BY customer_id) > 30 THEN 'At Risk' ELSE 'Active' END AS status_flag
FROM calculated_gaps;


-- @block 10. CTE with Multiple Levels
WITH monthly_customer_revenue AS (
    SELECT o.customer_id, 
           strftime('%Y-%m', o.order_date) AS order_month,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id, order_month
),
customer_segmentation AS (
    SELECT customer_id, 
           order_month,
           CASE WHEN revenue > 10000 THEN 'High'
                WHEN revenue BETWEEN 5000 AND 10000 THEN 'Medium'
                ELSE 'Low' END AS tier
    FROM monthly_customer_revenue
)
SELECT order_month, 
       tier, 
       COUNT(customer_id) AS customer_count
FROM customer_segmentation
GROUP BY order_month, tier
ORDER BY order_month ASC, tier DESC;


-- @block 11. NTILE for Segmentation
WITH customer_ltv AS (
    SELECT o.customer_id,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
),
quartiled AS (
    SELECT customer_id, 
           total_value,
           NTILE(4) OVER (ORDER BY total_value DESC) AS quartile
    FROM customer_ltv
)
SELECT customer_id, 
       ROUND(total_value, 2) AS total_value, 
       quartile,
       CASE WHEN quartile = 1 THEN 'Platinum'
            WHEN quartile = 2 THEN 'Gold'
            WHEN quartile = 3 THEN 'Silver'
            ELSE 'Bronze' END AS quartile_label
FROM quartiled;


-- @block 12. Year-over-Year Comparison
WITH monthly_rev AS (
    SELECT CAST(strftime('%Y', o.order_date) AS INTEGER) AS r_year,
           CAST(strftime('%m', o.order_date) AS INTEGER) AS r_month,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY r_year, r_month
)
SELECT cur.r_year AS year, 
       cur.r_month AS month, 
       ROUND(cur.revenue, 2) AS revenue,
       ROUND(prev.revenue, 2) AS "prev year revenue",
       ROUND(((cur.revenue - COALESCE(prev.revenue, 0)) / NULLIF(prev.revenue, 0)) * 100.0, 2) AS "yoy growth percent"
FROM monthly_rev cur
LEFT JOIN monthly_rev prev ON cur.r_year = prev.r_year + 1 AND cur.r_month = prev.r_month;


-- @block 13. First/Last Value Analysis
WITH first_last_indices AS (
    SELECT o.customer_id, 
           p.category, 
           o.order_date,
           ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date ASC, oi.item_id ASC) AS rn_first,
           ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC, oi.item_id DESC) AS rn_last
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
),
first_cat AS (SELECT customer_id, category AS first_category FROM first_last_indices WHERE rn_first = 1),
last_cat  AS (SELECT customer_id, category AS most_recent_category FROM first_last_indices WHERE rn_last = 1)
SELECT f.customer_id, 
       f.first_category, 
       l.most_recent_category,
       CASE WHEN f.first_category <> l.most_recent_category THEN 'Yes' ELSE 'No' END AS category_shift
FROM first_cat f
JOIN last_cat l ON f.customer_id = l.customer_id;


-- @block 14. Cumulative Distribution
WITH customer_spend AS (
    SELECT o.customer_id,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
),
running_calculations AS (
    SELECT customer_id, 
           revenue,
           SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue
    FROM customer_spend
)
SELECT customer_id,
       ROUND(revenue, 2) AS revenue,
       ROUND(cumulative_revenue, 2) AS cumulative_revenue,
       ROUND((cumulative_revenue / (SELECT SUM(revenue) FROM customer_spend)) * 100.0, 2) AS cumulative_percent
FROM running_calculations;


-- @block 15. Complex CTE: Cohort Analysis
WITH user_cohorts AS (
    SELECT customer_id, strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
order_months AS (
    SELECT DISTINCT o.customer_id,
           (CAST(strftime('%Y', o.order_date) AS INTEGER) - CAST(strftime('%Y', c.registration_date) AS INTEGER)) * 12 +
           (CAST(strftime('%m', o.order_date) AS INTEGER) - CAST(strftime('%m', c.registration_date) AS INTEGER)) AS month_number
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE month_number >= 0
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS total_users
    FROM customers GROUP BY cohort_month
),
retention_counts AS (
    SELECT uc.cohort_month, om.month_number, COUNT(DISTINCT om.customer_id) AS active_users
    FROM order_months om
    JOIN user_cohorts uc ON om.customer_id = uc.customer_id
    GROUP BY uc.cohort_month, om.month_number
)
SELECT rc.cohort_month, 
       cs.total_users, 
       rc.month_number, 
       rc.active_users,
       ROUND((CAST(rc.active_users AS REAL) / cs.total_users) * 100.0, 2) AS retention_rate
FROM retention_counts rc
JOIN cohort_sizes cs ON rc.cohort_month = cs.cohort_month
WHERE rc.month_number <= 3
ORDER BY rc.cohort_month, rc.month_number;


-- @block 16. Self-Join with Window Function
SELECT oi1.product_id AS product_a, 
       oi2.product_id AS product_b, 
       COUNT(*) AS "times bought together"
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
GROUP BY product_a, product_b
ORDER BY "times bought together" DESC
LIMIT 20;