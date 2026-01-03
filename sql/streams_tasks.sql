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
-- Stream 1: Track New Stock Data (Base Table)
-- ============================================================================
-- Captures all INSERT operations on raw_stock table

CREATE OR REPLACE STREAM stock_raw_stream 
ON TABLE raw_stock
COMMENT = 'Tracks new stock data insertions for processing';

-- ============================================================================
-- Task 1: Process New Stock Data
-- ============================================================================

CREATE OR REPLACE TASK process_new_stock
    WAREHOUSE = compute_wh
    SCHEDULE = '60 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('stock_raw_stream')
AS
BEGIN
    INSERT INTO user_actions (user_name, action_type, action_data)
    SELECT 'SYSTEM', 'DATA_INGESTION', OBJECT_CONSTRUCT('records', COUNT(*))
    FROM stock_raw_stream WHERE METADATA$ACTION = 'INSERT';
END;

-- ============================================================================
-- Task 2: Generate Critical Alerts
-- ============================================================================

CREATE OR REPLACE TASK generate_critical_alerts
    WAREHOUSE = compute_wh
    SCHEDULE = '5 MINUTE'
AS
BEGIN
    INSERT INTO alert_log (location, item, alert_type, alert_message)
    SELECT h."location", h."item", h.stock_status, 'Stock alert triggered'
    FROM stock_health h
    WHERE h.stock_status IN ('OUT_OF_STOCK', 'CRITICAL', 'WARNING');
END;

-- ============================================================================
-- Task 3: Daily Summary Report
-- ============================================================================

CREATE OR REPLACE TASK daily_summary_report
    WAREHOUSE = compute_wh
    SCHEDULE = 'USING CRON 0 8 * * * Asia/Kolkata'
AS
BEGIN
    INSERT INTO user_actions (user_name, action_type, action_data)
    SELECT 'SYSTEM', 'DAILY_SUMMARY', OBJECT_CONSTRUCT('count', COUNT(*))
    FROM stock_health;
END;

-- ============================================================================
-- Task 4: Cleanup Old Alerts
-- ============================================================================

CREATE OR REPLACE TASK cleanup_old_alerts
    WAREHOUSE = compute_wh
    SCHEDULE = 'USING CRON 0 2 * * 0 Asia/Kolkata'
AS
BEGIN
    DELETE FROM alert_log WHERE acknowledged = TRUE;
END;

-- ============================================================================
-- Task Dependencies Logic
-- ============================================================================

CREATE OR REPLACE TASK root_data_pipeline
    WAREHOUSE = compute_wh
    SCHEDULE = '1 HOUR'
AS
    SELECT 'Pipeline started' AS status;

CREATE OR REPLACE TASK child_alert_generation
    WAREHOUSE = compute_wh
    AFTER root_data_pipeline
AS
BEGIN
    SELECT 'Alerts generated' AS status;
END;

-- ============================================================================
-- Task Management Commands
-- ============================================================================

-- Safely suspend the root of the graph before resuming children
ALTER TASK root_data_pipeline SUSPEND;

-- Resume independent tasks
ALTER TASK process_new_stock RESUME;
ALTER TASK generate_critical_alerts RESUME;
ALTER TASK daily_summary_report RESUME;
ALTER TASK cleanup_old_alerts RESUME;

-- Resume child tasks in the graph
ALTER TASK child_alert_generation RESUME;

-- Resume the root task LAST to activate the graph
ALTER TASK root_data_pipeline RESUME;

-- ============================================================================
-- Monitoring
-- ============================================================================
SHOW STREAMS;
SHOW TASKS;
