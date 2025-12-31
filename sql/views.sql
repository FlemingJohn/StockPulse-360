-- ============================================================================
-- Fix Views - Use Correct Column Names with Quotes
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- Drop existing views
DROP VIEW IF EXISTS stock_risk;
DROP VIEW IF EXISTS critical_alerts;
DROP VIEW IF EXISTS procurement_export;
DROP VIEW IF EXISTS location_summary;
DROP VIEW IF EXISTS item_performance;

-- ============================================================================
-- View 1: Stock Risk (FIXED)
-- ============================================================================

CREATE OR REPLACE VIEW stock_risk AS
SELECT
    h.location AS LOCATION,
    h.item AS ITEM,
    h.current_stock AS CURRENT_STOCK,
    h.avg_daily_usage AS AVG_DAILY_USAGE,
    h.safety_stock AS SAFETY_STOCK,
    h.days_until_stockout AS DAYS_UNTIL_STOCKOUT,
    h.stock_status AS STOCK_STATUS,
    h.health_score AS HEALTH_SCORE,
    h.last_updated_date AS LAST_UPDATED_DATE
FROM stock_health h;

-- ============================================================================
-- View 2: Critical Alerts (FIXED)
-- ============================================================================

CREATE OR REPLACE VIEW critical_alerts AS
SELECT
    h.location AS LOCATION,
    h.item AS ITEM,
    h.current_stock AS CURRENT_STOCK,
    h.avg_daily_usage AS AVG_DAILY_USAGE,
    h.days_until_stockout AS DAYS_UNTIL_STOCKOUT,
    h.stock_status AS STOCK_STATUS,
    CASE
        WHEN h.stock_status = 'OUT_OF_STOCK' THEN 'URGENT: ' || h.item || ' is out of stock at ' || h.location
        WHEN h.stock_status = 'CRITICAL' THEN 'CRITICAL: ' || h.item || ' at ' || h.location || ' will run out in ' || h.days_until_stockout || ' days'
        WHEN h.stock_status = 'WARNING' THEN 'WARNING: ' || h.item || ' at ' || h.location || ' is running low'
        ELSE 'INFO: Stock level acceptable'
    END AS ALERT_MESSAGE,
    h.last_updated_date AS LAST_UPDATED_DATE
FROM stock_health h
WHERE h.stock_status IN ('OUT_OF_STOCK', 'CRITICAL', 'WARNING');

-- ============================================================================
-- View 3: Procurement Export (FIXED)
-- ============================================================================

CREATE OR REPLACE VIEW procurement_export AS
SELECT
    r.location AS "Location",
    r.item AS "Item Name",
    r.current_stock AS "Current Stock",
    r.reorder_quantity AS "Quantity to Order",
    r.priority AS "Priority",
    r.days_until_stockout AS "Order Within (Days)",
    r.estimated_cost AS "Estimated Cost (₹)",
    r.last_updated_date AS "Last Updated"
FROM reorder_recommendations r
ORDER BY 
    CASE r.priority
        WHEN 'URGENT' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        ELSE 4
    END,
    r.days_until_stockout;

-- ============================================================================
-- View 4: Location Summary (FIXED)
-- ============================================================================

CREATE OR REPLACE VIEW location_summary AS
SELECT
    h.location AS LOCATION,
    COUNT(*) AS TOTAL_ITEMS,
    SUM(CASE WHEN h.stock_status = 'OUT_OF_STOCK' THEN 1 ELSE 0 END) AS OUT_OF_STOCK_COUNT,
    SUM(CASE WHEN h.stock_status = 'CRITICAL' THEN 1 ELSE 0 END) AS CRITICAL_COUNT,
    SUM(CASE WHEN h.stock_status = 'WARNING' THEN 1 ELSE 0 END) AS WARNING_COUNT,
    SUM(CASE WHEN h.stock_status = 'LOW' THEN 1 ELSE 0 END) AS LOW_COUNT,
    SUM(CASE WHEN h.stock_status = 'HEALTHY' THEN 1 ELSE 0 END) AS HEALTHY_COUNT,
    ROUND(AVG(h.health_score), 1) AS AVG_HEALTH_SCORE,
    MAX(h.last_updated_date) AS LAST_UPDATED
FROM stock_health h
GROUP BY h.location;

-- ============================================================================
-- View 5: Item Performance (FIXED)
-- ============================================================================

CREATE OR REPLACE VIEW item_performance AS
SELECT
    s.item AS ITEM,
    COUNT(DISTINCT s.location) AS LOCATIONS_STOCKED,
    SUM(s.current_stock) AS TOTAL_STOCK_ALL_LOCATIONS,
    ROUND(AVG(s.avg_daily_usage), 2) AS AVG_USAGE_PER_LOCATION,
    SUM(s.total_issued) AS TOTAL_ISSUED_7DAYS,
    CASE
        WHEN AVG(s.avg_daily_usage) > (SELECT AVG(avg_daily_usage) FROM stock_stats) THEN 'HIGH_DEMAND'
        WHEN AVG(s.avg_daily_usage) < (SELECT AVG(avg_daily_usage) FROM stock_stats) / 2 THEN 'LOW_DEMAND'
        ELSE 'NORMAL'
    END AS DEMAND_CATEGORY,
    SUM(CASE WHEN h.stock_status IN ('OUT_OF_STOCK', 'CRITICAL') THEN 1 ELSE 0 END) AS CRITICAL_LOCATIONS,
    MAX(s.last_updated_date) AS LAST_UPDATED
FROM stock_stats s
JOIN stock_health h ON s.location = h.location AND s.item = h.item
GROUP BY s.item
ORDER BY TOTAL_ISSUED_7DAYS DESC;
