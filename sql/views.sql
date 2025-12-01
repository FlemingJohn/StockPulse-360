-- ============================================================================
-- StockPulse 360 - Views
-- ============================================================================
-- Views provide simplified, business-focused data access
-- Reference: https://docs.snowflake.com/en/sql-reference/sql/create-view
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- ============================================================================
-- View 1: Stock Risk Dashboard
-- ============================================================================
-- Simplified view for the main dashboard heatmap

CREATE OR REPLACE VIEW stock_risk AS
SELECT
    location,
    item,
    current_stock,
    avg_daily_usage,
    lead_time_days,
    days_until_stockout,
    stock_status,
    health_score,
    
    -- Color coding for heatmap
    CASE stock_status
        WHEN 'OUT_OF_STOCK' THEN '#8B0000'  -- Dark Red
        WHEN 'CRITICAL' THEN '#DC143C'       -- Crimson
        WHEN 'WARNING' THEN '#FFA500'        -- Orange
        WHEN 'LOW' THEN '#FFD700'            -- Gold
        WHEN 'HEALTHY' THEN '#32CD32'        -- Lime Green
        ELSE '#808080'                       -- Gray
    END AS status_color,
    
    last_updated_date
FROM stock_health
ORDER BY health_score ASC, location, item;

-- ============================================================================
-- View 2: Critical Alerts
-- ============================================================================
-- Shows only items requiring immediate attention

CREATE OR REPLACE VIEW critical_alerts AS
SELECT
    location,
    item,
    current_stock,
    avg_daily_usage,
    days_until_stockout,
    stock_status,
    
    -- Alert message
    CASE
        WHEN stock_status = 'OUT_OF_STOCK' THEN 
            '🚨 OUT OF STOCK - Immediate action required!'
        WHEN stock_status = 'CRITICAL' THEN 
            '⚠️ CRITICAL - Stock out in ' || ROUND(days_until_stockout, 1) || ' days'
        WHEN stock_status = 'WARNING' THEN 
            '⚡ WARNING - Low stock, reorder soon'
    END AS alert_message,
    
    last_updated_date
FROM stock_health
WHERE stock_status IN ('OUT_OF_STOCK', 'CRITICAL', 'WARNING')
ORDER BY 
    CASE stock_status
        WHEN 'OUT_OF_STOCK' THEN 1
        WHEN 'CRITICAL' THEN 2
        WHEN 'WARNING' THEN 3
    END,
    days_until_stockout ASC NULLS FIRST;

-- ============================================================================
-- View 3: Procurement Export
-- ============================================================================
-- Ready-to-export view for procurement teams

CREATE OR REPLACE VIEW procurement_export AS
SELECT
    r.location AS "Location",
    r.item AS "Item Name",
    h.current_stock AS "Current Stock",
    h.avg_daily_usage AS "Avg Daily Usage",
    r.recommended_order_qty AS "Recommended Order Qty",
    r.order_urgency_days AS "Order Within (Days)",
    h.lead_time_days AS "Supplier Lead Time",
    h.stock_status AS "Status",
    
    -- Estimated cost (placeholder - can be joined with price table)
    r.recommended_order_qty * 10 AS "Estimated Cost (₹)",
    
    CURRENT_DATE() AS "Report Date"
FROM reorder_recommendations r
JOIN stock_health h 
    ON r.location = h.location 
    AND r.item = h.item
WHERE r.recommended_order_qty > 0
ORDER BY r.priority_score DESC;

-- ============================================================================
-- View 4: Location Summary
-- ============================================================================
-- High-level summary by location for management dashboard

CREATE OR REPLACE VIEW location_summary AS
SELECT
    location,
    COUNT(DISTINCT item) AS total_items,
    
    -- Status breakdown
    SUM(CASE WHEN stock_status = 'OUT_OF_STOCK' THEN 1 ELSE 0 END) AS out_of_stock_count,
    SUM(CASE WHEN stock_status = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_count,
    SUM(CASE WHEN stock_status = 'WARNING' THEN 1 ELSE 0 END) AS warning_count,
    SUM(CASE WHEN stock_status = 'LOW' THEN 1 ELSE 0 END) AS low_count,
    SUM(CASE WHEN stock_status = 'HEALTHY' THEN 1 ELSE 0 END) AS healthy_count,
    
    -- Overall health score
    ROUND(AVG(health_score), 1) AS avg_health_score,
    
    -- Overall status
    CASE
        WHEN SUM(CASE WHEN stock_status = 'OUT_OF_STOCK' THEN 1 ELSE 0 END) > 0 THEN 'CRITICAL'
        WHEN SUM(CASE WHEN stock_status = 'CRITICAL' THEN 1 ELSE 0 END) > 0 THEN 'NEEDS_ATTENTION'
        WHEN SUM(CASE WHEN stock_status = 'WARNING' THEN 1 ELSE 0 END) > 2 THEN 'MONITOR'
        ELSE 'GOOD'
    END AS overall_status,
    
    MAX(last_updated_date) AS last_updated
FROM stock_health
GROUP BY location
ORDER BY avg_health_score ASC;

-- ============================================================================
-- View 5: Item Performance
-- ============================================================================
-- Track item consumption patterns across all locations

CREATE OR REPLACE VIEW item_performance AS
SELECT
    s.item,
    COUNT(DISTINCT s.location) AS locations_stocked,
    SUM(s.current_stock) AS total_stock_all_locations,
    ROUND(AVG(s.avg_daily_usage), 2) AS avg_usage_per_location,
    SUM(s.total_issued) AS total_issued_7days,
    
    -- Identify high-demand items
    CASE
        WHEN AVG(s.avg_daily_usage) > (SELECT AVG(avg_daily_usage) FROM stock_stats) THEN 'HIGH_DEMAND'
        WHEN AVG(s.avg_daily_usage) < (SELECT AVG(avg_daily_usage) FROM stock_stats) / 2 THEN 'LOW_DEMAND'
        ELSE 'NORMAL'
    END AS demand_category,
    
    -- Risk summary
    SUM(CASE WHEN h.stock_status IN ('OUT_OF_STOCK', 'CRITICAL') THEN 1 ELSE 0 END) AS critical_locations,
    
    MAX(s.last_updated_date) AS last_updated
FROM stock_stats s
JOIN stock_health h ON s.location = h.location AND s.item = h.item
GROUP BY s.item
ORDER BY total_issued_7days DESC;

-- ============================================================================
-- View 6: Daily Stock Movement
-- ============================================================================
-- Track daily changes for trend analysis

CREATE OR REPLACE VIEW daily_stock_movement AS
SELECT
    record_date,
    location,
    item,
    opening_stock,
    received,
    issued,
    closing_stock,
    
    -- Daily change
    closing_stock - opening_stock AS net_change,
    
    -- Percentage change
    CASE 
        WHEN opening_stock > 0 THEN 
            ROUND(((closing_stock - opening_stock) / opening_stock) * 100, 2)
        ELSE NULL
    END AS pct_change,
    
    -- Movement type
    CASE
        WHEN issued > received THEN 'DEPLETING'
        WHEN received > issued THEN 'BUILDING'
        ELSE 'STABLE'
    END AS movement_type
FROM stock_raw
ORDER BY record_date DESC, location, item;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Show all views
SHOW VIEWS;

-- Test each view
SELECT * FROM stock_risk LIMIT 5;
SELECT * FROM critical_alerts LIMIT 5;
SELECT * FROM procurement_export LIMIT 5;
SELECT * FROM location_summary;
SELECT * FROM item_performance LIMIT 5;
SELECT * FROM daily_stock_movement LIMIT 5;
