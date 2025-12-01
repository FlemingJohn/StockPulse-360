# ❄️ Snowflake CLI Workflow Guide

The **Snowflake CLI (`snow`)** is a powerful tool that can automate about **80%** of this project's workflow. This guide explains what it can do and where you still need standard Python.

## ✅ What Snowflake CLI Can Do (The "Cloud" Side)

### 1. Manage Connections
Instead of editing `config.py`, you can manage credentials securely:
```bash
# Add a connection
snow connection add stockpulse \
  --account="<org>-<account>" \
  --user="<username>" \
  --password="<password>" \
  --warehouse="compute_wh" \
  --database="stockpulse_db" \
  --schema="public"

# Test connection
snow connection test -c stockpulse
```

### 2. Execute SQL Scripts (Setup)
You can run all your setup scripts directly without opening the Snowflake UI:
```bash
# Create tables
snow sql -f sql/create_tables.sql -c stockpulse

# Load data
snow sql -f sql/load_data.sql -c stockpulse

# Create logic
snow sql -f sql/dynamic_tables.sql -c stockpulse
snow sql -f sql/views.sql -c stockpulse
snow sql -f sql/supplier_integration.sql -c stockpulse
```

### 3. Deploy Streamlit App
You can push your dashboard to the cloud so others can use it:
```bash
snow streamlit deploy --project "StockPulse 360" --file streamlit/app.py -c stockpulse
```

### 4. Manage Resources
Check your tables and views:
```bash
snow object list view -c stockpulse
snow object list table -c stockpulse
```

---

## ❌ What Snowflake CLI Cannot Do (The "Local" Side)

The CLI is for **Snowflake resources**. It does not replace Python for **local development tasks**:

1.  **Running Local Streamlit**:
    *   To test your app *before* deploying, you still need:
        ```bash
        py -m streamlit run streamlit/app.py
        ```

2.  **Running Standalone Python Scripts**:
    *   Scripts like `python/alert_sender.py` or `python/forecast_model.py` run on your *laptop*, not inside Snowflake.
    *   You must run them with Python:
        ```bash
        py python/alert_sender.py
        ```

    > **💡 Pro Tip:** You *could* convert these scripts into **Snowpark Stored Procedures**. If you do that, then `snow` CAN run them!

---

## 🚀 The "All-In-Snowflake" Workflow

If you want to use `snow` for **everything**, here is the ideal workflow:

1.  **Setup**: Use `snow sql` to build the database.
2.  **Develop**: Use `py -m streamlit` to test changes locally.
3.  **Deploy**: Use `snow streamlit deploy` to publish.
4.  **Automate**: Instead of running local Python scripts, use `snow sql` to create **Tasks** that run automatically in the cloud.

```sql
-- Example: Automate forecasting inside Snowflake
CREATE OR REPLACE TASK daily_forecast
WAREHOUSE = compute_wh
SCHEDULE = 'USING CRON 0 6 * * * UTC'
AS
CALL generate_forecast_procedure();
```
