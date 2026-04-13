-- ─────────────────────────────────────────
-- RETAIL ANALYTICS - SQL ANALYSIS
-- ─────────────────────────────────────────

-- 1. OVERALL BUSINESS SUMMARY
-- Quick snapshot of the entire business
SELECT
    COUNT(DISTINCT invoice) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(*) AS total_items_sold,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS avg_order_value
FROM transactions;

-- ─────────────────────────────────────────

-- 2. REVENUE BY COUNTRY
-- Which countries are driving the most revenue?
SELECT
    country,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT invoice) AS total_orders,
    ROUND(SUM(total_amount), 2) AS total_revenue
FROM transactions
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;

-- ─────────────────────────────────────────

-- 3. TOP 10 BEST SELLING PRODUCTS
-- What products make the most money?
SELECT
    stock_code,
    description,
    SUM(quantity) AS total_quantity_sold,
    ROUND(SUM(total_amount), 2) AS total_revenue
FROM transactions
GROUP BY stock_code, description
ORDER BY total_revenue DESC
LIMIT 10;

-- ─────────────────────────────────────────

-- 4. MONTHLY REVENUE TREND
-- How does revenue change month by month?
SELECT
    DATE_FORMAT(invoice_date, '%Y-%m') AS month,
    COUNT(DISTINCT invoice) AS total_orders,
    ROUND(SUM(total_amount), 2) AS monthly_revenue
FROM transactions
GROUP BY month
ORDER BY month;

-- ─────────────────────────────────────────

-- 5. REVENUE BY DAY OF WEEK
-- Which days of the week are busiest?
SELECT
    DAYNAME(invoice_date) AS day_of_week,
    COUNT(DISTINCT invoice) AS total_orders,
    ROUND(SUM(total_amount), 2) AS total_revenue
FROM transactions
GROUP BY day_of_week
ORDER BY total_revenue DESC;

-- ─────────────────────────────────────────

-- 6. TOP 10 CUSTOMERS BY REVENUE
-- Who are our most valuable customers?
SELECT
    customer_id,
    country,
    COUNT(DISTINCT invoice) AS total_orders,
    ROUND(SUM(total_amount), 2) AS total_spent
FROM transactions
GROUP BY customer_id, country
ORDER BY total_spent DESC
LIMIT 10;

-- ─────────────────────────────────────────

-- 7. AVERAGE ORDER VALUE BY COUNTRY
-- Where do customers spend the most per order?
SELECT
    country,
    COUNT(DISTINCT invoice) AS total_orders,
    ROUND(SUM(total_amount) / COUNT(DISTINCT invoice), 2) AS avg_order_value
FROM transactions
GROUP BY country
ORDER BY avg_order_value DESC
LIMIT 10; 