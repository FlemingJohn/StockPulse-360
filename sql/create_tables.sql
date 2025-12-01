-- ============================================================================
-- StockPulse 360 - Base Table Creation
-- ============================================================================
-- This script creates the foundational tables for the stock monitoring system
-- Reference: https://docs.snowflake.com/en/sql-reference/sql/create-table
-- ============================================================================

-- Create database and schema if not exists
CREATE DATABASE IF NOT EXISTS stockpulse_db;
USE DATABASE stockpulse_db;

CREATE SCHEMA IF NOT EXISTS public;
USE SCHEMA public;

-- ============================================================================
-- Main Stock Raw Data Table
-- ============================================================================
-- Stores daily stock entries from hospitals, ration shops, and NGOs
-- This is the source of truth for all stock movements

CREATE OR REPLACE TABLE stock_raw (
    location STRING NOT NULL COMMENT 'Hospital/Ration Shop/NGO location name',
    item STRING NOT NULL COMMENT 'Medicine/Food item name',
    opening_stock NUMBER(10,2) NOT NULL COMMENT 'Stock at start of day',
    received NUMBER(10,2) DEFAULT 0 COMMENT 'Quantity received during the day',
    issued NUMBER(10,2) DEFAULT 0 COMMENT 'Quantity issued/consumed during the day',
    closing_stock NUMBER(10,2) NOT NULL COMMENT 'Stock at end of day',
    lead_time_days NUMBER(3,0) NOT NULL COMMENT 'Days needed to restock from supplier',
    record_date DATE NOT NULL COMMENT 'Date of this stock record',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
    CONSTRAINT pk_stock_raw PRIMARY KEY (location, item, record_date)
) COMMENT = 'Raw daily stock data from all locations';

-- ============================================================================
-- Create Stage for CSV Upload
-- ============================================================================
-- Reference: https://docs.snowflake.com/en/sql-reference/sql/create-stage

CREATE OR REPLACE STAGE stock_stage
    FILE_FORMAT = (
        TYPE = CSV
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
        FIELD_DELIMITER = ','
        TRIM_SPACE = TRUE
        ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
    )
    COMMENT = 'Stage for uploading stock CSV files';

-- ============================================================================
-- Forecast Output Table
-- ============================================================================
-- Stores AI-generated demand forecasts from Snowpark Python

CREATE OR REPLACE TABLE forecast_output (
    location STRING NOT NULL,
    item STRING NOT NULL,
    forecast_date DATE NOT NULL,
    demand_next_7_days NUMBER(10,2) COMMENT '7-day demand forecast',
    demand_next_14_days NUMBER(10,2) COMMENT '14-day demand forecast',
    confidence_score NUMBER(3,2) COMMENT 'Forecast confidence (0-1)',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_forecast PRIMARY KEY (location, item, forecast_date)
) COMMENT = 'AI-generated demand forecasts';

-- ============================================================================
-- Alert Log Table
-- ============================================================================
-- Tracks all generated alerts for audit and notification purposes

CREATE OR REPLACE TABLE alert_log (
    alert_id NUMBER AUTOINCREMENT,
    location STRING NOT NULL,
    item STRING NOT NULL,
    alert_type STRING NOT NULL COMMENT 'CRITICAL, WARNING, INFO',
    alert_message STRING,
    days_left NUMBER(5,2),
    recommended_reorder_qty NUMBER(10,2),
    alert_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by STRING,
    acknowledged_at TIMESTAMP_NTZ,
    CONSTRAINT pk_alert_log PRIMARY KEY (alert_id)
) COMMENT = 'Log of all stock alerts generated';

-- ============================================================================
-- User Actions Table (Unistore)
-- ============================================================================
-- Stores user interactions like approval requests, reorder confirmations

CREATE OR REPLACE TABLE user_actions (
    action_id NUMBER AUTOINCREMENT,
    user_name STRING,
    action_type STRING COMMENT 'REORDER_APPROVED, ALERT_DISMISSED, etc.',
    location STRING,
    item STRING,
    action_data VARIANT COMMENT 'JSON data for flexible action details',
    action_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_user_actions PRIMARY KEY (action_id)
) COMMENT = 'User actions and approvals (Unistore)';

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Show all created tables
SHOW TABLES;

-- Verify table structure
DESC TABLE stock_raw;
DESC TABLE forecast_output;
DESC TABLE alert_log;
DESC TABLE user_actions;
