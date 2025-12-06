-- ============================================================================
-- StockPulse 360 - Streams and Tasks
-- ============================================================================
-- Streams track changes, Tasks automate workflows
-- Reference: https://docs.snowflake.com/en/user-guide/streams
-- Reference: https://docs.snowflake.com/en/user-guide/tasks-intro
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- ============================================================================
-- Stream 1: Track New Stock Data
-- ============================================================================
-- Captures all INSERT operations on raw_stock table

CREATE OR REPLACE STREAM stock_raw_stream 
ON TABLE raw_stock
COMMENT = 'Tracks new stock data insertions for processing';

-- ============================================================================
-- Stream 2: Track Alert Changes
-- ============================================================================
-- Monitors changes in stock health for alert generation

CREATE OR REPLACE STREAM stock_health_stream
ON TABLE stock_health
COMMENT = 'Tracks changes in stock health status';

-- ============================================================================
-- Task 1: Process New Stock Data
-- ============================================================================
-- Runs every hour to process new stock entries
-- This task would trigger any custom processing logic

CREATE OR REPLACE TASK process_new_stock
    WAREHOUSE = compute_wh
    SCHEDULE = '60 MINUTE'
    COMMENT = 'Process newly inserted stock data'
WHEN
    SYSTEM$STREAM_HAS_DATA('stock_raw_stream')
AS
BEGIN
    -- Log new records count
    INSERT INTO user_actions (
        user_name,
        action_type,
        action_data,
        action_timestamp
    )
    SELECT
        'SYSTEM',
        'DATA_INGESTION',
        OBJECT_CONSTRUCT(
            'records_processed', COUNT(*),
            'locations', ARRAY_AGG(DISTINCT "location"),
            'items', ARRAY_AGG(DISTINCT "item")
        ),
        CURRENT_TIMESTAMP()
    FROM stock_raw_stream
    WHERE METADATA$ACTION = 'INSERT';
END;

-- ============================================================================
-- Task 2: Generate Critical Alerts
-- ============================================================================
-- Runs every 30 minutes to check for critical stock situations

CREATE OR REPLACE TASK generate_critical_alerts
    WAREHOUSE = compute_wh
    SCHEDULE = '30 MINUTE'
    COMMENT = 'Generate alerts for critical stock levels'
AS
BEGIN
    -- Insert new alerts for critical items
    INSERT INTO alert_log (
        location,
        item,
        alert_type,
        alert_message,
        days_left,
        recommended_reorder_qty
    )
    SELECT
        h."location",
        h."item",
        h.stock_status AS alert_type,
        CASE
            WHEN h.stock_status = 'OUT_OF_STOCK' THEN 
                'URGENT: ' || h."item" || ' is OUT OF STOCK at ' || h."location"
            WHEN h.stock_status = 'CRITICAL' THEN 
                'CRITICAL: ' || h."item" || ' at ' || h."location" || ' will run out in ' || 
                ROUND(h.days_until_stockout, 1) || ' days'
            WHEN h.stock_status = 'WARNING' THEN 
                'WARNING: ' || h."item" || ' at ' || h."location" || ' is running low'
        END AS alert_message,
        h.days_until_stockout,
        r.recommended_order_qty
    FROM stock_health h
    LEFT JOIN reorder_recommendations r 
        ON h."location" = r."location" AND h."item" = r."item"
    WHERE h.stock_status IN ('OUT_OF_STOCK', 'CRITICAL', 'WARNING')
    AND NOT EXISTS (
        -- Avoid duplicate alerts within last 24 hours
        SELECT 1 FROM alert_log a
        WHERE a.location = h."location"
        AND a.item = h."item"
        AND a.alert_type = h.stock_status
        AND a.alert_date > DATEADD(hour, -24, CURRENT_TIMESTAMP())
        AND a.acknowledged = FALSE
    );
END;

-- ============================================================================
-- Task 3: Daily Summary Report
-- ============================================================================
-- Runs daily at 8 AM to generate summary reports

CREATE OR REPLACE TASK daily_summary_report
    WAREHOUSE = compute_wh
    SCHEDULE = 'USING CRON 0 8 * * * Asia/Kolkata'
    COMMENT = 'Generate daily summary report at 8 AM IST'
AS
BEGIN
    -- Log daily summary
    INSERT INTO user_actions (
        user_name,
        action_type,
        action_data,
        action_timestamp
    )
    SELECT
        'SYSTEM',
        'DAILY_SUMMARY',
        OBJECT_CONSTRUCT(
            'total_locations', COUNT(DISTINCT location),
            'total_items', COUNT(DISTINCT item),
            'critical_count', SUM(CASE WHEN stock_status = 'CRITICAL' THEN 1 ELSE 0 END),
            'warning_count', SUM(CASE WHEN stock_status = 'WARNING' THEN 1 ELSE 0 END),
            'healthy_count', SUM(CASE WHEN stock_status = 'HEALTHY' THEN 1 ELSE 0 END),
            'avg_health_score', ROUND(AVG(health_score), 2),
            'total_reorder_recommendations', (SELECT COUNT(*) FROM reorder_recommendations)
        ),
        CURRENT_TIMESTAMP()
    FROM stock_health;
END;

-- ============================================================================
-- Task 4: Cleanup Old Alerts
-- ============================================================================
-- Runs weekly to archive acknowledged alerts older than 30 days

CREATE OR REPLACE TASK cleanup_old_alerts
    WAREHOUSE = compute_wh
    SCHEDULE = 'USING CRON 0 2 * * 0 Asia/Kolkata'  -- Sunday 2 AM
    COMMENT = 'Archive old acknowledged alerts'
AS
BEGIN
    -- Delete acknowledged alerts older than 30 days
    DELETE FROM alert_log
    WHERE acknowledged = TRUE
    AND acknowledged_at < DATEADD(day, -30, CURRENT_TIMESTAMP());
END;

-- ============================================================================
-- Task Dependencies (Optional)
-- ============================================================================
-- Create a root task and child tasks for complex workflows

-- Root task (runs first)
CREATE OR REPLACE TASK root_data_pipeline
    WAREHOUSE = compute_wh
    SCHEDULE = '1 HOUR'
    COMMENT = 'Root task for data pipeline'
AS
    SELECT 'Pipeline started' AS status;

-- Child task (runs after root task)
CREATE OR REPLACE TASK child_alert_generation
    WAREHOUSE = compute_wh
    AFTER root_data_pipeline
    COMMENT = 'Generate alerts after data processing'
AS
BEGIN
    -- Alert generation logic
    SELECT 'Alerts generated' AS status;
END;

-- ============================================================================
-- Task Management Commands
-- ============================================================================

-- Resume all tasks (they are created in SUSPENDED state)
ALTER TASK process_new_stock RESUME;
ALTER TASK generate_critical_alerts RESUME;
ALTER TASK daily_summary_report RESUME;
ALTER TASK cleanup_old_alerts RESUME;

-- Suspend tasks (for maintenance)
-- ALTER TASK process_new_stock SUSPEND;
-- ALTER TASK generate_critical_alerts SUSPEND;
-- ALTER TASK daily_summary_report SUSPEND;
-- ALTER TASK cleanup_old_alerts SUSPEND;

-- ============================================================================
-- Monitoring Queries
-- ============================================================================

-- Show all streams
SHOW STREAMS;

-- Check stream contents
SELECT * FROM stock_raw_stream LIMIT 10;

-- Show all tasks
SHOW TASKS;

-- Check task execution history
SELECT
    name,
    state,
    scheduled_time,
    completed_time,
    error_code,
    error_message
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE name IN (
    'PROCESS_NEW_STOCK',
    'GENERATE_CRITICAL_ALERTS',
    'DAILY_SUMMARY_REPORT',
    'CLEANUP_OLD_ALERTS'
)
ORDER BY scheduled_time DESC
LIMIT 20;

-- Check if stream has data
SELECT SYSTEM$STREAM_HAS_DATA('stock_raw_stream');

-- View recent alerts
SELECT * FROM alert_log 
ORDER BY alert_date DESC 
LIMIT 10;
