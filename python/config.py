"""
StockPulse 360 - Snowflake Configuration
Reference: https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect
"""

import os
from typing import Dict

# ============================================================================
# Snowflake Connection Configuration
# ============================================================================
# IMPORTANT: Replace these with your actual Snowflake credentials
# For production, use environment variables or Snowflake config file

SNOWFLAKE_CONFIG: Dict[str, str] = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT", "your_account_identifier"),
    "user": os.getenv("SNOWFLAKE_USER", "your_username"),
    "password": os.getenv("SNOWFLAKE_PASSWORD", "your_password"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "compute_wh"),
    "database": os.getenv("SNOWFLAKE_DATABASE", "stockpulse_db"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA", "public"),
    "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
}

# ============================================================================
# Alternative: Using Snowflake Config File
# ============================================================================
# Create a file at ~/.snowflake/config with:
# [connections.stockpulse]
# account = your_account
# user = your_user
# password = your_password
# warehouse = compute_wh
# database = stockpulse_db
# schema = public

# Then use: connection_name = "stockpulse"

# ============================================================================
# Application Settings
# ============================================================================

APP_CONFIG = {
    "forecast_days": [7, 14],  # Forecast horizons
    "alert_threshold_critical": 0.3,  # 30% of safety stock
    "alert_threshold_warning": 0.5,   # 50% of safety stock
    "min_data_points": 3,  # Minimum days of data for forecasting
}

# ============================================================================
# Helper Function to Get Session
# ============================================================================

def get_snowflake_session():
    """
    Create and return a Snowflake session.
    Reference: https://docs.snowflake.com/en/developer-guide/snowpark/python/creating-session
    """
    from snowflake.snowpark import Session
    
    try:
        session = Session.builder.configs(SNOWFLAKE_CONFIG).create()
        print(f"✅ Connected to Snowflake: {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")
        return session
    except Exception as e:
        print(f"❌ Failed to connect to Snowflake: {e}")
        raise

def get_snowflake_connector():
    """
    Create and return a Snowflake connector (for non-Snowpark operations).
    """
    import snowflake.connector
    
    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        print(f"✅ Connected to Snowflake via connector")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to Snowflake: {e}")
        raise
