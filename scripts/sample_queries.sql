-- Quick Reference SQL Queries for Olist Database

-- ========================================
-- 1. BASIC DATA EXPLORATION
-- ========================================

-- Get total counts
SELECT 'orders' as table_name, COUNT(*) as count FROM orders
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items;

-- Order status distribution
SELECT order_status, COUNT(*) as count
FROM orders
GROUP BY order_status
ORDER BY count DESC;

-- ========================================
-- 2. SALES ANALYSIS
-- ========================================

-- Total revenue by month
SELECT 
    DATE_TRUNC('month', order_purchase_timestamp) as month,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.price) as total_revenue,
    AVG(oi.price) as avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month DESC;

-- Top 10 selling products
SELECT 
    p.product_id,
    p.product_category_name,
    t.product_category_name_english,
    COUNT(*) as times_sold,
    SUM(oi.price) as total_revenue,
    AVG(oi.price) as avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t ON p.product_category_name = t.product_category_name
GROUP BY p.product_id, p.product_category_name, t.product_category_name_english
ORDER BY times_sold DESC
LIMIT 10;

-- Top 10 product categories by revenue
SELECT 
    COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') as category,
    COUNT(DISTINCT oi.order_id) as total_orders,
    SUM(oi.price) as total_revenue,
    AVG(oi.price) as avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t ON p.product_category_name = t.product_category_name
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;

-- ========================================
-- 3. CUSTOMER ANALYSIS
-- ========================================

-- Top 10 cities by number of customers
SELECT 
    customer_city,
    customer_state,
    COUNT(DISTINCT customer_id) as total_customers,
    COUNT(*) as total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY customer_city, customer_state
ORDER BY total_customers DESC
LIMIT 10;

-- Customer repeat purchase rate
SELECT 
    customer_unique_id,
    COUNT(DISTINCT o.order_id) as total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY customer_unique_id
HAVING COUNT(DISTINCT o.order_id) > 1
ORDER BY total_orders DESC;

-- ========================================
-- 4. REVIEW ANALYSIS
-- ========================================

-- Average review score by product category
SELECT 
    COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') as category,
    COUNT(*) as total_reviews,
    AVG(r.review_score) as avg_score,
    COUNT(CASE WHEN r.review_score >= 4 THEN 1 END) * 100.0 / COUNT(*) as positive_pct
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t ON p.product_category_name = t.product_category_name
GROUP BY category
HAVING COUNT(*) > 50
ORDER BY avg_score DESC;

-- Low-rated orders with comments
SELECT 
    r.order_id,
    r.review_score,
    r.review_comment_title,
    r.review_comment_message,
    c.customer_city,
    c.customer_state
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE r.review_score <= 2 
  AND r.review_comment_message IS NOT NULL
ORDER BY r.review_creation_date DESC
LIMIT 20;

-- ========================================
-- 5. DELIVERY PERFORMANCE
-- ========================================

-- Average delivery time by state
SELECT 
    c.customer_state,
    COUNT(*) as total_deliveries,
    AVG(EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))/86400) as avg_delivery_days,
    AVG(EXTRACT(EPOCH FROM (o.order_estimated_delivery_date - o.order_delivered_customer_date))/86400) as avg_early_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
  AND o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY avg_delivery_days DESC;

-- Late deliveries
SELECT 
    o.order_id,
    c.customer_city,
    c.customer_state,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_estimated_delivery_date))/86400 as days_late
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date > o.order_estimated_delivery_date
  AND o.order_status = 'delivered'
ORDER BY days_late DESC
LIMIT 20;

-- ========================================
-- 6. SELLER PERFORMANCE
-- ========================================

-- Top 10 sellers by revenue
SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) as total_orders,
    COUNT(*) as total_items_sold,
    SUM(oi.price) as total_revenue,
    AVG(oi.price) as avg_item_price
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
GROUP BY s.seller_id, s.seller_city, s.seller_state
ORDER BY total_revenue DESC
LIMIT 10;

-- ========================================
-- 7. PAYMENT ANALYSIS
-- ========================================

-- Payment type distribution
SELECT 
    payment_type,
    COUNT(*) as total_transactions,
    SUM(payment_value) as total_value,
    AVG(payment_value) as avg_value,
    AVG(payment_installments) as avg_installments
FROM order_payments
GROUP BY payment_type
ORDER BY total_transactions DESC;

-- Orders with multiple payment methods
SELECT 
    order_id,
    COUNT(*) as payment_methods_used,
    SUM(payment_value) as total_paid
FROM order_payments
GROUP BY order_id
HAVING COUNT(*) > 1
ORDER BY payment_methods_used DESC;

-- ========================================
-- 8. GEOGRAPHIC ANALYSIS
-- ========================================

-- Sales by state
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT c.customer_id) as total_customers,
    SUM(oi.price) as total_revenue,
    AVG(oi.price) as avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_revenue DESC;

-- ========================================
-- 9. COMPLEX ANALYTICAL QUERIES
-- ========================================

-- Product performance with review scores
SELECT 
    COALESCE(t.product_category_name_english, p.product_category_name) as category,
    COUNT(DISTINCT oi.order_id) as orders,
    SUM(oi.price) as revenue,
    AVG(oi.price) as avg_price,
    AVG(r.review_score) as avg_review,
    COUNT(CASE WHEN r.review_score = 5 THEN 1 END) * 100.0 / NULLIF(COUNT(r.review_score), 0) as five_star_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t ON p.product_category_name = t.product_category_name
LEFT JOIN order_reviews r ON oi.order_id = r.order_id
GROUP BY category
HAVING COUNT(DISTINCT oi.order_id) > 100
ORDER BY revenue DESC;

-- Customer cohort analysis (monthly)
SELECT 
    DATE_TRUNC('month', first_purchase) as cohort_month,
    COUNT(DISTINCT customer_unique_id) as customers,
    SUM(total_orders) as total_orders,
    SUM(total_spent) as total_revenue
FROM (
    SELECT 
        c.customer_unique_id,
        MIN(o.order_purchase_timestamp) as first_purchase,
        COUNT(DISTINCT o.order_id) as total_orders,
        SUM(oi.price) as total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_unique_id
) cohorts
GROUP BY cohort_month
ORDER BY cohort_month;
