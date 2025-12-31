-- ============================================================================
-- StockPulse 360 - Advanced AI/ML Views
-- ============================================================================
-- Views for Cortex AI forecasts, anomalies, and seasonal patterns
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- ============================================================================
-- View 1: AI Forecast Comparison
-- ============================================================================
-- Compare different forecasting methods

CREATE OR REPLACE VIEW ai_forecast_comparison AS
SELECT
    COALESCE(f.location, c.location, s.location) AS location,
    COALESCE(f.item, c.item, s.item) AS item,
    COALESCE(f.forecast_date, c.forecast_date, s.forecast_date) AS forecast_date,
    
    -- Basic forecast (from forecast_model.py)
    f.demand_next_7_days AS basic_forecast_7day,
    
    -- Cortex AI forecast
    c.forecasted_usage AS cortex_ai_forecast,
    c.confidence_interval_lower AS cortex_lower_bound,
    c.confidence_interval_upper AS cortex_upper_bound,
    
    -- Seasonal forecast
    s.forecasted_usage AS seasonal_forecast,
    s.seasonal_factor,
    
    -- Ensemble forecast (average of all methods)
    ROUND(
        (COALESCE(f.demand_next_7_days / 7, 0) + 
         COALESCE(c.forecasted_usage, 0) + 
         COALESCE(s.forecasted_usage, 0)) / 3,
        2
    ) AS ensemble_forecast,
    
    CURRENT_TIMESTAMP() AS generated_at
FROM forecast_output f
FULL OUTER JOIN cortex_forecasts c 
    ON f.location = c.location 
    AND f.item = c.item
FULL OUTER JOIN seasonal_forecasts s
    ON f.location = s.location 
    AND f.item = s.item;

-- ============================================================================
-- View 2: Anomaly Dashboard
-- ============================================================================
-- Consolidated view of all anomalies

CREATE OR REPLACE VIEW anomaly_dashboard AS
SELECT
    location,
    item,
    anomaly_date,
    anomaly_type,
    severity,
    description,
    detected_at,
    DATEDIFF(day, detected_at, CURRENT_TIMESTAMP()) AS days_since_detection,
    CASE
        WHEN anomaly_type IN ('NEGATIVE_STOCK', 'OVER_ISSUED', 'CALCULATION_MISMATCH') 
        THEN 'DATA_QUALITY'
        WHEN anomaly_type IN ('SUDDEN_STOCK_CHANGE', 'SUDDEN_USAGE_CHANGE') 
        THEN 'SUDDEN_CHANGE'
        WHEN anomaly_type = 'USAGE_ANOMALY' 
        THEN 'STATISTICAL_OUTLIER'
        ELSE 'OTHER'
    END AS anomaly_category
FROM anomaly_log
WHERE detected_at >= DATEADD(day, -30, CURRENT_DATE())
ORDER BY detected_at DESC;

-- ============================================================================
-- View 3: Seasonal Insights
-- ============================================================================
-- Key insights from seasonal analysis

CREATE OR REPLACE VIEW seasonal_insights AS
WITH weekly_avg AS (
    SELECT
        location,
        item,
        DAYOFWEEK(forecast_date) AS day_of_week,
        AVG(forecasted_usage) AS avg_usage,
        AVG(seasonal_factor) AS avg_seasonal_factor
    FROM seasonal_forecasts
    GROUP BY location, item, day_of_week
),
peak_days AS (
    SELECT
        location,
        item,
        day_of_week,
        avg_usage,
        avg_seasonal_factor,
        ROW_NUMBER() OVER (PARTITION BY location, item ORDER BY avg_usage DESC) AS usage_rank
    FROM weekly_avg
)
SELECT
    location,
    item,
    CASE day_of_week
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS peak_day_name,
    ROUND(avg_usage, 2) AS peak_usage,
    ROUND(avg_seasonal_factor, 2) AS peak_seasonal_factor,
    CASE
        WHEN avg_seasonal_factor > 1.2 THEN 'HIGH_DEMAND_DAY'
        WHEN avg_seasonal_factor < 0.8 THEN 'LOW_DEMAND_DAY'
        ELSE 'NORMAL_DAY'
    END AS demand_pattern
FROM peak_days
WHERE usage_rank = 1;

-- ============================================================================
-- View 4: AI-Enhanced Stock Risk
-- ============================================================================
-- Combines traditional risk metrics with AI forecasts

CREATE OR REPLACE VIEW ai_enhanced_stock_risk AS
SELECT
    h.location,
    h.item,
    h.current_stock,
    h.avg_daily_usage,
    h.days_until_stockout,
    h.stock_status,
    h.health_score,
    
    -- AI forecasts
    f.ensemble_forecast AS ai_predicted_usage,
    f.cortex_ai_forecast,
    f.seasonal_forecast,
    
    -- AI-adjusted days until stockout
    CASE
        WHEN f.ensemble_forecast > 0 THEN
            ROUND(h.current_stock / f.ensemble_forecast, 2)
        ELSE h.days_until_stockout
    END AS ai_adjusted_days_left,
    
    -- Anomaly flag
    CASE
        WHEN EXISTS (
            SELECT 1 FROM anomaly_log a
            WHERE a.location = h.location
            AND a.item = h.item
            AND a.detected_at >= DATEADD(day, -7, CURRENT_DATE())
        ) THEN TRUE
        ELSE FALSE
    END AS has_recent_anomaly,
    
    -- Seasonal risk flag
    s.demand_pattern AS seasonal_pattern,
    
    CURRENT_TIMESTAMP() AS calculated_at
FROM stock_health h
LEFT JOIN ai_forecast_comparison f
    ON h.location = f.location
    AND h.item = f.item
LEFT JOIN seasonal_insights s
    ON h.location = s.location
    AND h.item = s.item;

-- ============================================================================
-- View 5: ML Model Performance
-- ============================================================================
-- Track forecast accuracy over time

CREATE OR REPLACE VIEW ml_model_performance AS
WITH actual_usage AS (
    SELECT
        location,
        item,
        last_updated_date AS record_date,
        issued_qty AS actual_value
    FROM raw_stock
),
forecast_comparison AS (
    SELECT
        a.location,
        a.item,
        a.record_date,
        a.actual_value,
        f.basic_forecast_7day / 7 AS basic_forecast,
        f.cortex_ai_forecast,
        f.seasonal_forecast,
        f.ensemble_forecast,
        
        -- Calculate errors
        ABS(a.actual_value - (f.basic_forecast_7day / 7)) AS basic_error,
        ABS(a.actual_value - f.cortex_ai_forecast) AS cortex_error,
        ABS(a.actual_value - f.seasonal_forecast) AS seasonal_error,
        ABS(a.actual_value - f.ensemble_forecast) AS ensemble_error
    FROM actual_usage a
    JOIN ai_forecast_comparison f
        ON a.location = f.location
        AND a.item = f.item
        AND a.record_date = f.forecast_date
)
SELECT
    location,
    item,
    COUNT(*) AS forecast_count,
    
    -- Mean Absolute Error (MAE)
    ROUND(AVG(basic_error), 2) AS basic_mae,
    ROUND(AVG(cortex_error), 2) AS cortex_mae,
    ROUND(AVG(seasonal_error), 2) AS seasonal_mae,
    ROUND(AVG(ensemble_error), 2) AS ensemble_mae,
    
    -- Best performing model
    CASE
        WHEN AVG(cortex_error) <= AVG(basic_error) 
        THEN 'CORTEX_AI'
        WHEN AVG(seasonal_error) <= AVG(basic_error)
        THEN 'SEASONAL'
        ELSE 'ENSEMBLE'
    END AS best_model
FROM forecast_comparison
GROUP BY location, item;
