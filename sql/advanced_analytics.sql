-- ============================================================================
-- StockPulse 360 - Advanced Analytics Views
-- ============================================================================
-- ABC Analysis and Stockout Impact Analysis
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- ============================================================================
-- View 1: ABC Analysis
-- ============================================================================
-- Classify items by importance based on value contribution
-- A: Top 20% (High-value, critical items)
-- B: Next 30% (Medium-value items)
-- C: Bottom 50% (Low-value items)

CREATE OR REPLACE VIEW abc_analysis AS
WITH item_value AS (
    SELECT
        item,
        location,
        SUM("issued_qty") AS total_issued,
        -- Using estimated unit prices (can be replaced with actual price table)
        CASE "item"
            WHEN 'Insulin' THEN 500  -- High value
            WHEN 'ORS' THEN 10       -- Low value
            WHEN 'Paracetamol' THEN 5 -- Low value
            ELSE 10
        END AS unit_price
    FROM raw_stock
    GROUP BY "item", "location"
),
item_total_value AS (
    SELECT
        item,
        SUM(total_issued * unit_price) AS total_value,
        SUM(total_issued) AS total_quantity,
        COUNT(DISTINCT location) AS locations_count
    FROM item_value
    GROUP BY item
)
SELECT
    item,
    total_value,
    total_quantity,
    locations_count,
    ROUND((total_value / SUM(total_value) OVER ()) * 100, 2) AS value_percentage,
    ROUND((total_quantity / SUM(total_quantity) OVER ()) * 100, 2) AS quantity_percentage,
    CASE
        WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.2 THEN 'A'
        WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.5 THEN 'B'
        ELSE 'C'
    END AS abc_category,
    CASE
        WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.2 THEN 'HIGH_VALUE_CRITICAL'
        WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.5 THEN 'MEDIUM_VALUE'
        ELSE 'LOW_VALUE'
    END AS category_description,
    -- Priority for inventory management
    CASE
        WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.2 THEN 1
        WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.5 THEN 2
        ELSE 3
    END AS management_priority
FROM item_total_value
ORDER BY total_value DESC;

-- ============================================================================
-- View 2: ABC Analysis by Location
-- ============================================================================
-- ABC classification per location for localized inventory management

CREATE OR REPLACE VIEW abc_analysis_by_location AS
WITH location_item_value AS (
    SELECT
        location,
        item,
        SUM("issued_qty") AS total_issued,
        CASE "item"
            WHEN 'Insulin' THEN 500
            WHEN 'ORS' THEN 10
            WHEN 'Paracetamol' THEN 5
            ELSE 10
        END AS unit_price
    FROM raw_stock
    GROUP BY "location", "item"
),
location_value AS (
    SELECT
        location,
        item,
        total_issued * unit_price AS total_value,
        total_issued
    FROM location_item_value
)
SELECT
    location,
    item,
    total_value,
    total_issued,
    CASE
        WHEN PERCENT_RANK() OVER (PARTITION BY location ORDER BY total_value DESC) <= 0.2 THEN 'A'
        WHEN PERCENT_RANK() OVER (PARTITION BY location ORDER BY total_value DESC) <= 0.5 THEN 'B'
        ELSE 'C'
    END AS abc_category,
    ROUND((total_value / SUM(total_value) OVER (PARTITION BY location)) * 100, 2) AS location_value_pct
FROM location_value
ORDER BY location, total_value DESC;

-- ============================================================================
-- View 3: Stockout Impact Analysis
-- ============================================================================
-- Calculate potential patient/beneficiary impact from stock-outs

CREATE OR REPLACE VIEW stockout_impact AS
SELECT
    h.location,
    h.item,
    h.current_stock,
    h.avg_daily_usage,
    h.days_until_stockout,
    h.stock_status,
    
    -- Patient impact calculations
    ROUND(h.avg_daily_usage * h.days_until_stockout, 0) AS patients_affected_until_stockout,
    
    -- If stock runs out, daily impact
    ROUND(h.avg_daily_usage, 0) AS daily_patients_affected,
    
    -- Weekly impact if stock-out occurs
    ROUND(h.avg_daily_usage * 7, 0) AS weekly_patients_affected,
    
    -- Severity based on item criticality and impact
    CASE
        WHEN h.item = 'Insulin' AND h.stock_status IN ('OUT_OF_STOCK', 'CRITICAL') THEN 'LIFE_THREATENING'
        WHEN h.item IN ('Insulin', 'ORS') AND h.stock_status = 'CRITICAL' THEN 'HIGH_SEVERITY'
        WHEN h.stock_status = 'CRITICAL' THEN 'MODERATE_SEVERITY'
        WHEN h.stock_status = 'WARNING' THEN 'LOW_SEVERITY'
        ELSE 'MINIMAL'
    END AS impact_severity,
    
    -- ABC category for prioritization
    a.abc_category,
    a.management_priority,
    
    -- Combined priority score (lower = more urgent)
    CASE
        WHEN h.stock_status = 'OUT_OF_STOCK' THEN 1
        WHEN h.stock_status = 'CRITICAL' AND a.abc_category = 'A' THEN 2
        WHEN h.stock_status = 'CRITICAL' AND a.abc_category = 'B' THEN 3
        WHEN h.stock_status = 'CRITICAL' THEN 4
        WHEN h.stock_status = 'WARNING' AND a.abc_category = 'A' THEN 5
        ELSE 6
    END AS action_priority,
    
    h.last_updated_date
FROM stock_health h
LEFT JOIN abc_analysis a ON h."item" = a.item
WHERE h.stock_status IN ('OUT_OF_STOCK', 'CRITICAL', 'WARNING')
ORDER BY action_priority, patients_affected_until_stockout DESC;

-- ============================================================================
-- View 4: Critical Items Dashboard
-- ============================================================================
-- Combines ABC analysis with stock health for critical decision making

CREATE OR REPLACE VIEW critical_items_dashboard AS
SELECT
    h.location,
    h.item,
    a.abc_category,
    a.category_description,
    h.current_stock,
    h.avg_daily_usage,
    h.days_until_stockout,
    h.stock_status,
    h.health_score,
    
    -- Impact metrics
    s.patients_affected_until_stockout,
    s.daily_patients_affected,
    s.impact_severity,
    s.action_priority,
    
    -- Recommended action
    CASE
        WHEN h.stock_status = 'OUT_OF_STOCK' THEN 'EMERGENCY_ORDER_NOW'
        WHEN h.stock_status = 'CRITICAL' AND a.abc_category = 'A' THEN 'URGENT_REORDER_24H'
        WHEN h.stock_status = 'CRITICAL' THEN 'REORDER_48H'
        WHEN h.stock_status = 'WARNING' AND a.abc_category = 'A' THEN 'SCHEDULE_REORDER'
        ELSE 'MONITOR'
    END AS recommended_action,
    
    -- Reorder quantity
    r.recommended_order_qty,
    r.order_urgency_days,
    
    CURRENT_TIMESTAMP() AS report_generated_at
FROM stock_health h
LEFT JOIN abc_analysis a ON h."item" = a.item
LEFT JOIN stockout_impact s ON h."location" = s.location AND h."item" = s.item
LEFT JOIN reorder_recommendations r ON h."location" = r."location" AND h."item" = r."item"
WHERE h.stock_status IN ('OUT_OF_STOCK', 'CRITICAL', 'WARNING', 'LOW')
   OR a.abc_category = 'A'
ORDER BY s.action_priority, a.management_priority, h.health_score;

-- ============================================================================
-- View 5: ABC Summary Statistics
-- ============================================================================
-- Summary statistics for ABC categories

CREATE OR REPLACE VIEW abc_summary_statistics AS
SELECT
    abc_category,
    COUNT(*) AS item_count,
    ROUND(SUM(total_value), 2) AS total_value,
    ROUND(SUM(total_quantity), 0) AS total_quantity,
    ROUND(AVG(value_percentage), 2) AS avg_value_percentage,
    ROUND(SUM(value_percentage), 2) AS cumulative_value_percentage,
    ROUND(SUM(quantity_percentage), 2) AS cumulative_quantity_percentage,
    
    -- Pareto principle validation (80-20 rule)
    CASE
        WHEN abc_category = 'A' AND SUM(value_percentage) >= 70 THEN 'FOLLOWS_PARETO'
        WHEN abc_category = 'A' THEN 'MODERATE_CONCENTRATION'
        ELSE 'N/A'
    END AS pareto_validation
FROM abc_analysis
GROUP BY abc_category
ORDER BY abc_category;

-- ============================================================================
-- View 6: Item Price Table (for reference)
-- ============================================================================
-- Create a reference table for item prices
-- This can be updated with actual prices

CREATE OR REPLACE TABLE IF NOT EXISTS item_prices (
    item STRING PRIMARY KEY,
    unit_price NUMBER(10,2),
    currency STRING DEFAULT 'INR',
    price_effective_date DATE DEFAULT CURRENT_DATE(),
    price_category STRING,
    COMMENT 'Reference prices for ABC analysis'
);

-- Insert default prices
MERGE INTO item_prices AS target
USING (
    SELECT 'Insulin' AS item, 500.00 AS unit_price, 'INR' AS currency, 'HIGH_VALUE' AS price_category
    UNION ALL
    SELECT 'ORS', 10.00, 'INR', 'LOW_VALUE'
    UNION ALL
    SELECT 'Paracetamol', 5.00, 'INR', 'LOW_VALUE'
) AS source
ON target.item = source.item
WHEN MATCHED THEN
    UPDATE SET 
        unit_price = source.unit_price,
        price_category = source.price_category
WHEN NOT MATCHED THEN
    INSERT (item, unit_price, currency, price_category)
    VALUES (source.item, source.unit_price, source.currency, source.price_category);

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Show ABC distribution
SELECT * FROM abc_summary_statistics;

-- Show critical items with ABC classification
SELECT * FROM critical_items_dashboard LIMIT 10;

-- Show stockout impact
SELECT * FROM stockout_impact ORDER BY action_priority LIMIT 10;

-- Show ABC analysis
SELECT * FROM abc_analysis;

-- Show ABC by location
SELECT * FROM abc_analysis_by_location WHERE location = 'Chennai';

-- ============================================================================
-- COST OPTIMIZATION VIEWS
-- ============================================================================

-- ============================================================================
-- View 7: Cost Savings Dashboard
-- ============================================================================
-- Track cost savings from waste reduction and optimized ordering

CREATE OR REPLACE VIEW cost_savings_dashboard AS
WITH waste_reduction AS (
    SELECT
        location,
        item,
        -- Calculate waste from overstocking
        CASE 
            WHEN current_stock > (avg_daily_usage * (lead_time_days + 14)) 
            THEN (current_stock - (avg_daily_usage * (lead_time_days + 14))) * 
                 (SELECT unit_price FROM item_prices WHERE item_prices.item = stock_health.item)
            ELSE 0
        END AS overstock_value
    FROM stock_health
),
emergency_avoidance AS (
    SELECT
        location,
        item,
        -- Emergency orders typically cost 30% more
        recommended_order_qty * 
        (SELECT unit_price FROM item_prices WHERE item_prices.item = reorder_recommendations.item) * 0.30 
        AS emergency_cost_avoided
    FROM reorder_recommendations
    WHERE order_urgency_days <= 2  -- Orders placed with 2+ days notice
),
bulk_opportunities AS (
    SELECT
        item,
        SUM(recommended_order_qty) AS total_qty_needed,
        (SELECT unit_price FROM item_prices WHERE item_prices.item = reorder_recommendations.item) AS current_price,
        -- Assume 10% discount for bulk orders
        SUM(recommended_order_qty) * 
        (SELECT unit_price FROM item_prices WHERE item_prices.item = reorder_recommendations.item) * 0.10 
        AS potential_bulk_savings
    FROM reorder_recommendations
    GROUP BY item
    HAVING SUM(recommended_order_qty) > 100  -- Bulk threshold
)
SELECT
    'Waste Reduction' AS savings_category,
    SUM(overstock_value) AS total_savings,
    COUNT(DISTINCT location || '-' || item) AS items_affected,
    'Reduced overstocking' AS description
FROM waste_reduction
WHERE overstock_value > 0

UNION ALL

SELECT
    'Emergency Order Avoidance',
    SUM(emergency_cost_avoided),
    COUNT(DISTINCT location || '-' || item),
    'Timely reorders prevent rush fees'
FROM emergency_avoidance

UNION ALL

SELECT
    'Bulk Purchase Opportunities',
    SUM(potential_bulk_savings),
    COUNT(DISTINCT item),
    'Volume discounts available'
FROM bulk_opportunities;

-- ============================================================================
-- View 8: Budget Tracking
-- ============================================================================
-- Monitor procurement spending against budget

CREATE OR REPLACE VIEW budget_tracking AS
WITH monthly_procurement AS (
    SELECT
        DATE_TRUNC('MONTH', CURRENT_DATE()) AS month,
        SUM(r.recommended_order_qty * p.unit_price) AS estimated_spend
    FROM reorder_recommendations r
    JOIN item_prices p ON r.item = p.item
),
budget_config AS (
    SELECT 100000 AS monthly_budget  -- ₹100,000 default budget
)
SELECT
    m.month,
    b.monthly_budget,
    m.estimated_spend,
    b.monthly_budget - m.estimated_spend AS remaining_budget,
    ROUND((m.estimated_spend / b.monthly_budget) * 100, 2) AS budget_utilization_pct,
    CASE
        WHEN m.estimated_spend > b.monthly_budget THEN 'OVER_BUDGET'
        WHEN m.estimated_spend > (b.monthly_budget * 0.9) THEN 'WARNING'
        WHEN m.estimated_spend > (b.monthly_budget * 0.75) THEN 'MODERATE'
        ELSE 'HEALTHY'
    END AS budget_status
FROM monthly_procurement m
CROSS JOIN budget_config b;

-- ============================================================================
-- View 9: Price Trend Analysis
-- ============================================================================
-- Track item price changes over time

CREATE OR REPLACE VIEW price_trend_analysis AS
WITH price_history AS (
    SELECT
        item,
        unit_price,
        price_date,
        LAG(unit_price) OVER (PARTITION BY item ORDER BY price_date) AS prev_price,
        LAG(price_date) OVER (PARTITION BY item ORDER BY price_date) AS prev_date
    FROM item_prices
)
SELECT
    item,
    unit_price AS current_price,
    prev_price,
    price_date AS current_date,
    prev_date,
    unit_price - prev_price AS price_change,
    ROUND(((unit_price - prev_price) / NULLIF(prev_price, 0)) * 100, 2) AS price_change_pct,
    CASE
        WHEN unit_price > prev_price THEN 'INCREASED'
        WHEN unit_price < prev_price THEN 'DECREASED'
        ELSE 'STABLE'
    END AS trend
FROM price_history
WHERE prev_price IS NOT NULL
ORDER BY ABS(price_change_pct) DESC;

-- ============================================================================
-- View 10: Cost Per Location
-- ============================================================================
-- Calculate total procurement cost by location

CREATE OR REPLACE VIEW cost_per_location AS
SELECT
    r.location,
    COUNT(DISTINCT r.item) AS items_to_order,
    SUM(r.recommended_order_qty) AS total_quantity,
    SUM(r.recommended_order_qty * p.unit_price) AS total_cost,
    AVG(p.unit_price) AS avg_item_price,
    MAX(r.recommended_order_qty * p.unit_price) AS highest_cost_item_value
FROM reorder_recommendations r
JOIN item_prices p ON r.item = p.item
GROUP BY r.location
ORDER BY total_cost DESC;

-- ============================================================================
-- View 11: ROI Analysis
-- ============================================================================
-- Calculate return on investment for stock management

CREATE OR REPLACE VIEW roi_analysis AS
WITH costs AS (
    SELECT
        SUM(recommended_order_qty * unit_price) AS total_procurement_cost
    FROM reorder_recommendations r
    JOIN item_prices p ON r.item = p.item
),
savings AS (
    SELECT SUM(total_savings) AS total_savings
    FROM cost_savings_dashboard
),
stockout_impact AS (
    SELECT 
        SUM(patients_affected_until_stockout * 100) AS stockout_cost_avoided  -- ₹100 per patient impact
    FROM stockout_impact
)
SELECT
    c.total_procurement_cost,
    s.total_savings,
    i.stockout_cost_avoided,
    s.total_savings + i.stockout_cost_avoided AS total_value_generated,
    ROUND(((s.total_savings + i.stockout_cost_avoided) / NULLIF(c.total_procurement_cost, 0)) * 100, 2) AS roi_percentage
FROM costs c
CROSS JOIN savings s
CROSS JOIN stockout_impact i;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Show cost savings
SELECT * FROM cost_savings_dashboard;

-- Show budget status
SELECT * FROM budget_tracking;

-- Show price trends
SELECT * FROM price_trend_analysis LIMIT 10;

-- Show cost by location
SELECT * FROM cost_per_location;

-- Show ROI
SELECT * FROM roi_analysis;

