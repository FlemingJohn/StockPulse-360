-- ============================================================================
-- StockPulse 360 - Unistore Implementation (Hybrid Tables)
-- ============================================================================
-- Unistore (Hybrid Tables) provides a single unified table type for transactional
-- and analytical workloads. It offers fast single-row lookups and enforcement
-- of primary key constraints, making it ideal for operational logs like alerts.
-- Reference: https://docs.snowflake.com/en/user-guide/tables-hybrid
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- ============================================================================
-- Hybrid Table: Alert Log (Transactional)
-- ============================================================================
-- Why Hybrid?
-- 1. High concurrency: Supports frequent inserts from the alert generation task.
-- 2. Fast single-row updates: Ideal for "Acknowledge Alert" actions by users.
-- 3. Primary Key Constraint: Strictly enforces unique Alert IDs.

CREATE OR REPLACE HYBRID TABLE alert_log_hybrid (
    alert_id NUMBER AUTOINCREMENT START 1 INCREMENT 1,
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
    
    -- Hybrid Tables REQUIRE a Primary Key
    CONSTRAINT pk_alert_log_hybrid PRIMARY KEY (alert_id)
    
    -- Secondary Indexes for fast lookups (Optional but recommended for operational queries)
    -- INDEX idx_location (location),
    -- INDEX idx_status (acknowledged)
) 
COMMENT = 'Unistore Hybrid Table for high-performance alert logging and acknowledgement';

-- ============================================================================
-- Verification
-- ============================================================================

SHOW HYBRID TABLES;

-- Test Transactional Performance
-- INSERT INTO alert_log_hybrid (location, item, alert_type, alert_message) 
-- VALUES ('Chennai General Hospital', 'Paracetamol', 'CRITICAL', 'Test Alert');

-- SELECT * FROM alert_log_hybrid WHERE alert_id = 1;

-- UPDATE alert_log_hybrid SET acknowledged = TRUE WHERE alert_id = 1;
