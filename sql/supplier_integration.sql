-- ============================================================================
-- StockPulse 360 - Supplier Integration
-- ============================================================================
-- Supplier management, lead time tracking, and purchase order generation
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- ============================================================================
-- Table 1: Suppliers
-- ============================================================================
-- Track supplier information, lead times, and reliability

CREATE OR REPLACE TABLE suppliers (
    supplier_id STRING PRIMARY KEY,
    supplier_name STRING NOT NULL,
    item STRING NOT NULL,
    avg_lead_time_days NUMBER(5,2) DEFAULT 7,
    reliability_score NUMBER(5,2) DEFAULT 100,  -- 0-100 scale
    unit_price NUMBER(10,2),
    contact_email STRING,
    contact_phone STRING,
    address STRING,
    last_delivery_date DATE,
    total_orders NUMBER DEFAULT 0,
    on_time_deliveries NUMBER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    COMMENT 'Supplier master data with performance tracking'
);

-- Insert sample suppliers
INSERT INTO suppliers (supplier_id, supplier_name, item, avg_lead_time_days, reliability_score, unit_price, contact_email, contact_phone, last_delivery_date, total_orders, on_time_deliveries)
VALUES
    ('SUP001', 'MedSupply Co.', 'Insulin', 3, 95, 500.00, 'orders@medsupply.com', '+91-9876543210', '2024-11-28', 50, 48),
    ('SUP002', 'QuickMeds Ltd', 'Insulin', 1, 85, 520.00, 'sales@quickmeds.com', '+91-9876543211', '2024-11-30', 30, 26),
    ('SUP003', 'PharmaDirect', 'ORS', 2, 98, 10.00, 'info@pharmadirect.com', '+91-9876543212', '2024-11-29', 100, 98),
    ('SUP004', 'HealthPlus Supplies', 'ORS', 4, 92, 9.50, 'orders@healthplus.com', '+91-9876543213', '2024-11-27', 45, 42),
    ('SUP005', 'MediCare Distributors', 'Paracetamol', 2, 96, 5.00, 'sales@medicare.com', '+91-9876543214', '2024-11-29', 80, 77),
    ('SUP006', 'FastPharma', 'Paracetamol', 1, 88, 5.20, 'orders@fastpharma.com', '+91-9876543215', '2024-11-30', 25, 22);

-- ============================================================================
-- View 1: Purchase Orders
-- ============================================================================
-- Auto-generate purchase orders from reorder recommendations

CREATE OR REPLACE VIEW purchase_orders AS
WITH best_suppliers AS (
    -- Select best supplier for each item based on reliability and lead time
    SELECT
        item,
        supplier_id,
        supplier_name,
        avg_lead_time_days,
        reliability_score,
        unit_price,
        contact_email,
        ROW_NUMBER() OVER (
            PARTITION BY item 
            ORDER BY reliability_score DESC, avg_lead_time_days ASC, unit_price ASC
        ) as supplier_rank
    FROM suppliers
    WHERE is_active = TRUE
)
SELECT
    CONCAT('PO-', TO_CHAR(CURRENT_DATE(), 'YYYYMMDD'), '-', 
           LPAD(ROW_NUMBER() OVER (ORDER BY r.location, r.item), 4, '0')) AS purchase_order_id,
    r.location,
    r.item,
    s.supplier_id,
    s.supplier_name,
    s.contact_email,
    r.recommended_order_qty AS order_quantity,
    s.unit_price,
    r.recommended_order_qty * s.unit_price AS total_cost,
    s.avg_lead_time_days,
    CURRENT_DATE() AS order_date,
    CURRENT_DATE() + s.avg_lead_time_days AS expected_delivery_date,
    r.order_urgency_days,
    CASE
        WHEN r.order_urgency_days < s.avg_lead_time_days THEN 'URGENT'
        WHEN r.order_urgency_days < (s.avg_lead_time_days * 1.5) THEN 'NORMAL'
        ELSE 'PLANNED'
    END AS order_priority,
    s.reliability_score,
    h.stock_status,
    CURRENT_TIMESTAMP() AS generated_at
FROM reorder_recommendations r
JOIN best_suppliers s ON r.item = s.item AND s.supplier_rank = 1
JOIN stock_health h ON r.location = h.location AND r.item = h.item;

-- ============================================================================
-- View 2: Supplier Performance Dashboard
-- ============================================================================
-- Track supplier reliability and performance metrics

CREATE OR REPLACE VIEW supplier_performance AS
SELECT
    supplier_id,
    supplier_name,
    item,
    avg_lead_time_days,
    reliability_score,
    unit_price,
    total_orders,
    on_time_deliveries,
    ROUND((on_time_deliveries * 100.0 / NULLIF(total_orders, 0)), 2) AS actual_on_time_pct,
    CASE
        WHEN reliability_score >= 95 THEN 'EXCELLENT'
        WHEN reliability_score >= 85 THEN 'GOOD'
        WHEN reliability_score >= 70 THEN 'AVERAGE'
        ELSE 'POOR'
    END AS performance_rating,
    DATEDIFF(day, last_delivery_date, CURRENT_DATE()) AS days_since_last_delivery,
    CASE
        WHEN DATEDIFF(day, last_delivery_date, CURRENT_DATE()) > 30 THEN 'INACTIVE'
        WHEN DATEDIFF(day, last_delivery_date, CURRENT_DATE()) > 14 THEN 'LOW_ACTIVITY'
        ELSE 'ACTIVE'
    END AS activity_status,
    is_active
FROM suppliers
ORDER BY reliability_score DESC, avg_lead_time_days ASC;

-- ============================================================================
-- View 3: Supplier Comparison
-- ============================================================================
-- Compare suppliers for the same item

CREATE OR REPLACE VIEW supplier_comparison AS
SELECT
    item,
    supplier_name,
    unit_price,
    avg_lead_time_days,
    reliability_score,
    -- Calculate score (higher is better)
    ROUND(
        (reliability_score * 0.5) +  -- 50% weight on reliability
        ((100 - (avg_lead_time_days * 10)) * 0.3) +  -- 30% weight on speed
        ((100 - ((unit_price / MIN(unit_price) OVER (PARTITION BY item) - 1) * 100)) * 0.2),  -- 20% weight on price
        2
    ) AS overall_score,
    RANK() OVER (PARTITION BY item ORDER BY 
        (reliability_score * 0.5) + 
        ((100 - (avg_lead_time_days * 10)) * 0.3) + 
        ((100 - ((unit_price / MIN(unit_price) OVER (PARTITION BY item) - 1) * 100)) * 0.2) DESC
    ) AS supplier_rank
FROM suppliers
WHERE is_active = TRUE
ORDER BY item, supplier_rank;

-- ============================================================================
-- View 4: Purchase Order Summary
-- ============================================================================
-- Summarize purchase orders by location and priority

CREATE OR REPLACE VIEW purchase_order_summary AS
SELECT
    location,
    order_priority,
    COUNT(*) AS total_orders,
    SUM(order_quantity) AS total_quantity,
    SUM(total_cost) AS total_cost,
    AVG(avg_lead_time_days) AS avg_delivery_days,
    MIN(expected_delivery_date) AS earliest_delivery,
    MAX(expected_delivery_date) AS latest_delivery,
    COUNT(DISTINCT supplier_id) AS unique_suppliers
FROM purchase_orders
GROUP BY location, order_priority
ORDER BY 
    CASE order_priority
        WHEN 'URGENT' THEN 1
        WHEN 'NORMAL' THEN 2
        WHEN 'PLANNED' THEN 3
    END,
    location;

-- ============================================================================
-- View 5: Supplier Cost Analysis
-- ============================================================================
-- Analyze total spending by supplier

CREATE OR REPLACE VIEW supplier_cost_analysis AS
SELECT
    s.supplier_id,
    s.supplier_name,
    COUNT(DISTINCT p.item) AS items_supplied,
    SUM(p.order_quantity) AS total_units_ordered,
    SUM(p.total_cost) AS total_spend,
    AVG(p.total_cost) AS avg_order_value,
    COUNT(*) AS total_purchase_orders,
    s.reliability_score,
    s.avg_lead_time_days
FROM purchase_orders p
JOIN suppliers s ON p.supplier_id = s.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.reliability_score, s.avg_lead_time_days
ORDER BY total_spend DESC;

-- ============================================================================
-- View 6: Delivery Schedule
-- ============================================================================
-- Track expected deliveries by date

CREATE OR REPLACE VIEW delivery_schedule AS
SELECT
    expected_delivery_date,
    location,
    item,
    supplier_name,
    order_quantity,
    total_cost,
    order_priority,
    stock_status,
    CASE
        WHEN expected_delivery_date = CURRENT_DATE() THEN 'TODAY'
        WHEN expected_delivery_date = CURRENT_DATE() + 1 THEN 'TOMORROW'
        WHEN expected_delivery_date <= CURRENT_DATE() + 7 THEN 'THIS_WEEK'
        ELSE 'LATER'
    END AS delivery_timeframe
FROM purchase_orders
ORDER BY expected_delivery_date, order_priority;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Show all suppliers
SELECT * FROM suppliers ORDER BY item, reliability_score DESC;

-- Show purchase orders
SELECT * FROM purchase_orders LIMIT 10;

-- Show supplier performance
SELECT * FROM supplier_performance;

-- Show supplier comparison
SELECT * FROM supplier_comparison WHERE item = 'Insulin';

-- Show purchase order summary
SELECT * FROM purchase_order_summary;

-- Show delivery schedule
SELECT * FROM delivery_schedule WHERE delivery_timeframe IN ('TODAY', 'TOMORROW');

-- Show cost analysis
SELECT * FROM supplier_cost_analysis;
