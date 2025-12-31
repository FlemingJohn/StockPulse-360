"""
StockPulse 360 - Snowflake Configuration
Reference: https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect
"""

import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Snowflake Connection Configuration
# ============================================================================
# IMPORTANT: Replace these with your actual Snowflake credentials
# For production, use environment variables or Snowflake config file

# Helper to get config from multiple sources
def get_config_value(key, env_key, default=None):
    # 1. Try Streamlit Secrets (for Cloud)
    try:
        import streamlit as st
        if "connections" in st.secrets and "snowflake" in st.secrets["connections"]:
            return st.secrets["connections"]["snowflake"].get(key)
    except:
        pass
        
    # 2. Try Environment Variable (for Local)
    return os.getenv(env_key, default)

SNOWFLAKE_CONFIG: Dict[str, str] = {
    "account": get_config_value("account", "SNOWFLAKE_ACCOUNT", "your_account"),
    "user": get_config_value("user", "SNOWFLAKE_USER", "your_user"),
    "password": get_config_value("password", "SNOWFLAKE_PASSWORD", "your_password"),
    "warehouse": get_config_value("warehouse", "SNOWFLAKE_WAREHOUSE", "compute_wh"),
    "database": get_config_value("database", "SNOWFLAKE_DATABASE", "stockpulse_db"),
    "schema": get_config_value("schema", "SNOWFLAKE_SCHEMA", "public"),
    "role": get_config_value("role", "SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
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
