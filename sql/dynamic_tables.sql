-- ============================================================================
-- StockPulse 360 - Dynamic Tables
-- ============================================================================
-- Dynamic Tables auto-refresh based on changes to source data
-- Reference: https://docs.snowflake.com/en/user-guide/dynamic-tables-intro
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- ============================================================================
-- Dynamic Table 1: Stock Statistics
-- ============================================================================
-- Automatically calculates key metrics for each location-item combination
-- Refreshes every 1 hour when source data changes

CREATE OR REPLACE DYNAMIC TABLE stock_stats
    TARGET_LAG = '1 hour'
    WAREHOUSE = compute_wh
    AS
SELECT
    location,
    item,
    -- Current stock levels
    MAX(closing_stock) AS current_stock,
    MAX(lead_time_days) AS lead_time_days,
    
    -- Usage statistics (last 7 days)
    AVG(issued) AS avg_daily_usage,
    MAX(issued) AS max_daily_usage,
    MIN(issued) AS min_daily_usage,
    STDDEV(issued) AS stddev_daily_usage,
    
    -- Receipt statistics
    AVG(received) AS avg_daily_received,
    SUM(received) AS total_received,
    
    -- Stock movement trends
    SUM(issued) AS total_issued,
    COUNT(*) AS days_tracked,
    
    -- Latest record date
    MAX(record_date) AS last_updated_date,
    CURRENT_TIMESTAMP() AS calculated_at
FROM stock_raw
WHERE record_date >= DATEADD(day, -7, CURRENT_DATE())  -- Last 7 days
GROUP BY location, item;

-- ============================================================================
-- Dynamic Table 2: Stock Health Indicators
-- ============================================================================
-- Calculates health scores and days-to-stockout predictions
-- Depends on stock_stats, so it refreshes after stock_stats updates

CREATE OR REPLACE DYNAMIC TABLE stock_health
    TARGET_LAG = '1 hour'
    WAREHOUSE = compute_wh
    AS
SELECT
    location,
    item,
    current_stock,
    avg_daily_usage,
    max_daily_usage,
    lead_time_days,
    
    -- Days until stock-out (based on average usage)
    CASE 
        WHEN avg_daily_usage > 0 THEN 
            ROUND(current_stock / avg_daily_usage, 2)
        ELSE NULL
    END AS days_until_stockout,
    
    -- Safety stock level (lead time + 2 buffer days)
    ROUND((avg_daily_usage * (lead_time_days + 2)), 2) AS safety_stock_level,
    
    -- Reorder point (lead time demand)
    ROUND((avg_daily_usage * lead_time_days), 2) AS reorder_point,
    
    -- Stock status classification
    CASE
        WHEN current_stock <= 0 THEN 'OUT_OF_STOCK'
        WHEN current_stock < (avg_daily_usage * lead_time_days) THEN 'CRITICAL'
        WHEN current_stock < (avg_daily_usage * (lead_time_days + 2)) THEN 'WARNING'
        WHEN current_stock < (avg_daily_usage * (lead_time_days + 5)) THEN 'LOW'
        ELSE 'HEALTHY'
    END AS stock_status,
    
    -- Stock health score (0-100)
    CASE
        WHEN avg_daily_usage = 0 THEN 100
        WHEN current_stock <= 0 THEN 0
        ELSE LEAST(100, ROUND((current_stock / (avg_daily_usage * (lead_time_days + 5))) * 100, 0))
    END AS health_score,
    
    last_updated_date,
    CURRENT_TIMESTAMP() AS calculated_at
FROM stock_stats
WHERE avg_daily_usage IS NOT NULL;

-- ============================================================================
-- Dynamic Table 3: Reorder Recommendations
-- ============================================================================
-- Generates actionable reorder recommendations

CREATE OR REPLACE DYNAMIC TABLE reorder_recommendations
    TARGET_LAG = '1 hour'
    WAREHOUSE = compute_wh
    AS
SELECT
    location,
    item,
    current_stock,
    avg_daily_usage,
    lead_time_days,
    days_until_stockout,
    stock_status,
    
    -- Recommended order quantity
    CASE
        WHEN stock_status IN ('CRITICAL', 'WARNING', 'LOW') THEN
            GREATEST(0, ROUND(
                (avg_daily_usage * (lead_time_days + 7))  -- 1 week buffer
                - current_stock, 
                0
            ))
        ELSE 0
    END AS recommended_order_qty,
    
    -- Order urgency (days)
    CASE
        WHEN stock_status = 'CRITICAL' THEN 1
        WHEN stock_status = 'WARNING' THEN 2
        WHEN stock_status = 'LOW' THEN 3
        ELSE NULL
    END AS order_urgency_days,
    
    -- Priority score (higher = more urgent)
    CASE
        WHEN stock_status = 'OUT_OF_STOCK' THEN 1000
        WHEN stock_status = 'CRITICAL' THEN 100 - health_score
        WHEN stock_status = 'WARNING' THEN 50 - (health_score / 2)
        ELSE 0
    END AS priority_score,
    
    CURRENT_TIMESTAMP() AS calculated_at
FROM stock_health
WHERE stock_status IN ('OUT_OF_STOCK', 'CRITICAL', 'WARNING', 'LOW')
ORDER BY priority_score DESC;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Show all dynamic tables
SHOW DYNAMIC TABLES;

-- Check refresh status
SELECT 
    name,
    state,
    target_lag,
    data_timestamp,
    refresh_mode
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY())
WHERE name IN ('STOCK_STATS', 'STOCK_HEALTH', 'REORDER_RECOMMENDATIONS')
ORDER BY data_timestamp DESC;

-- Preview results
SELECT * FROM stock_stats LIMIT 10;
SELECT * FROM stock_health ORDER BY health_score ASC LIMIT 10;
SELECT * FROM reorder_recommendations ORDER BY priority_score DESC LIMIT 10;
