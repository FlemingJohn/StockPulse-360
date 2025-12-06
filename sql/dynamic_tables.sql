-- ============================================================================
-- Fix Dynamic Tables - Use Correct Column Names
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- Drop existing dynamic tables
DROP DYNAMIC TABLE IF EXISTS stock_stats;
DROP DYNAMIC TABLE IF EXISTS stock_health;
DROP DYNAMIC TABLE IF EXISTS reorder_recommendations;

-- ============================================================================
-- Dynamic Table 1: Stock Statistics (FIXED)
-- ============================================================================

CREATE OR REPLACE DYNAMIC TABLE stock_stats
    TARGET_LAG = '1 minute'  -- Faster refresh for testing
    WAREHOUSE = compute_wh
    AS
SELECT
    "location",
    "item",
    -- Current stock levels
    MAX("current_stock") AS current_stock,
    3 AS lead_time_days,  -- Default lead time
    
    -- Usage statistics (last 7 days)
    AVG("issued_qty") AS avg_daily_usage,
    MAX("issued_qty") AS max_daily_usage,
    MIN("issued_qty") AS min_daily_usage,
    STDDEV("issued_qty") AS stddev_daily_usage,
    
    -- Receipt statistics
    AVG("received_qty") AS avg_daily_received,
    SUM("received_qty") AS total_received,
    
    -- Stock movement trends
    SUM("issued_qty") AS total_issued,
    COUNT(*) AS days_tracked,
    
    -- Latest record date
    MAX("last_updated_date") AS last_updated_date,
    CURRENT_TIMESTAMP() AS calculated_at
FROM raw_stock
WHERE "last_updated_date" >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY "location", "item";

-- ============================================================================
-- Dynamic Table 2: Stock Health Indicators (FIXED)
-- ============================================================================

CREATE OR REPLACE DYNAMIC TABLE stock_health
    TARGET_LAG = '1 minute'
    WAREHOUSE = compute_wh
    AS
SELECT
    s."location",
    s."item",
    s.current_stock,
    s.avg_daily_usage,
    s.lead_time_days,
    
    -- Safety stock calculation (2x average usage * lead time)
    ROUND(s.avg_daily_usage * s.lead_time_days * 2, 0) AS safety_stock,
    
    -- Days until stockout
    CASE
        WHEN s.avg_daily_usage > 0 THEN ROUND(s.current_stock / s.avg_daily_usage, 1)
        ELSE 999
    END AS days_until_stockout,
    
    -- Stock status
    CASE
        WHEN s.current_stock <= 0 THEN 'OUT_OF_STOCK'
        WHEN s.current_stock < (s.avg_daily_usage * s.lead_time_days * 0.5) THEN 'CRITICAL'
        WHEN s.current_stock < (s.avg_daily_usage * s.lead_time_days) THEN 'WARNING'
        WHEN s.current_stock < (s.avg_daily_usage * s.lead_time_days * 2) THEN 'LOW'
        ELSE 'HEALTHY'
    END AS stock_status,
    
    -- Health score (0-100)
    CASE
        WHEN s.current_stock <= 0 THEN 0
        WHEN s.avg_daily_usage > 0 THEN 
            LEAST(100, ROUND((s.current_stock / (s.avg_daily_usage * s.lead_time_days * 2)) * 100, 0))
        ELSE 100
    END AS health_score,
    
    s.last_updated_date,
    CURRENT_TIMESTAMP() AS calculated_at
FROM stock_stats s;

-- ============================================================================
-- Dynamic Table 3: Reorder Recommendations (FIXED)
-- ============================================================================

CREATE OR REPLACE DYNAMIC TABLE reorder_recommendations
    TARGET_LAG = '1 minute'
    WAREHOUSE = compute_wh
    AS
SELECT
    h."location",
    h."item",
    h.current_stock,
    h.avg_daily_usage,
    h.days_until_stockout,
    h.safety_stock,
    h.stock_status,
    
    -- Reorder quantity (bring to 30 days supply)
    GREATEST(0, ROUND((h.avg_daily_usage * 30) - h.current_stock, 0)) AS reorder_quantity,
    
    -- Order priority
    CASE
        WHEN h.stock_status = 'OUT_OF_STOCK' THEN 'URGENT'
        WHEN h.stock_status = 'CRITICAL' THEN 'HIGH'
        WHEN h.stock_status = 'WARNING' THEN 'MEDIUM'
        ELSE 'LOW'
    END AS priority,
    
    -- Estimated cost (placeholder - $10 per unit)
    GREATEST(0, ROUND((h.avg_daily_usage * 30) - h.current_stock, 0)) * 10 AS estimated_cost,
    
    h.last_updated_date,
    CURRENT_TIMESTAMP() AS calculated_at
FROM stock_health h
WHERE h.stock_status IN ('OUT_OF_STOCK', 'CRITICAL', 'WARNING');
