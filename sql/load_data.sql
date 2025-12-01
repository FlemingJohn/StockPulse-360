-- ============================================================================
-- StockPulse 360 - Data Loading Script
-- ============================================================================
-- This script loads CSV data into Snowflake tables
-- Reference: https://docs.snowflake.com/en/sql-reference/sql/copy-into-table
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- ============================================================================
-- Step 1: Upload CSV to Stage (Run from VS Code or SnowSQL)
-- ============================================================================
-- Option A: Using PUT command (from local machine via SnowSQL)
-- PUT file://d:/Projects/StockPulse 360/data/stock_data.csv @stock_stage AUTO_COMPRESS=FALSE;

-- Option B: Using Snowflake Web UI
-- Navigate to Data > Databases > STOCKPULSE_DB > PUBLIC > Stages > STOCK_STAGE
-- Click "Upload Files" and select stock_data.csv

-- ============================================================================
-- Step 2: Verify Files in Stage
-- ============================================================================
LIST @stock_stage;

-- ============================================================================
-- Step 3: Load Data from Stage to Table
-- ============================================================================
COPY INTO stock_raw (
    location,
    item,
    opening_stock,
    received,
    issued,
    closing_stock,
    lead_time_days,
    record_date
)
FROM @stock_stage/stock_data.csv
FILE_FORMAT = (
    TYPE = CSV
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    FIELD_DELIMITER = ','
    TRIM_SPACE = TRUE
)
ON_ERROR = CONTINUE
PURGE = FALSE;  -- Keep files in stage for re-loading if needed

-- ============================================================================
-- Step 4: Verify Loaded Data
-- ============================================================================
SELECT COUNT(*) AS total_records FROM stock_raw;

SELECT * FROM stock_raw LIMIT 10;

-- Check data by location
SELECT 
    location,
    COUNT(*) AS record_count,
    COUNT(DISTINCT item) AS unique_items,
    MIN(record_date) AS earliest_date,
    MAX(record_date) AS latest_date
FROM stock_raw
GROUP BY location
ORDER BY location;

-- Check for any data quality issues
SELECT 
    location,
    item,
    record_date,
    opening_stock,
    received,
    issued,
    closing_stock,
    -- Verify closing stock calculation
    (opening_stock + received - issued) AS calculated_closing,
    closing_stock AS actual_closing,
    CASE 
        WHEN ABS((opening_stock + received - issued) - closing_stock) > 0.01 
        THEN 'MISMATCH' 
        ELSE 'OK' 
    END AS validation_status
FROM stock_raw
WHERE ABS((opening_stock + received - issued) - closing_stock) > 0.01;

-- ============================================================================
-- Alternative: Direct Load from Local File (Snowpark Python)
-- ============================================================================
-- If you prefer to load via Python, see python/data_loader.py
