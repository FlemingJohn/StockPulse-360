# 🚀 Deployment Guide

This guide covers how to deploy the StockPulse 360 platform, including the database infrastructure and the Streamlit application.

---

## 🏗️ Phase 1: Database Infrastructure

Before deploying the app, you must create the Snowflake objects (Tables, Views, Streams, Tasks).

### Method A: Automated Script (Recommended)
We have a Python script to initialize everything.

1.  **Configure Credentials**:
    Ensure your `.env` or `python/config.py` is set up with a user who has `ACCOUNTADMIN` or sufficient privileges (CREATE DATABASE, CREATE WAREHOUSE).

2.  **Run the Initialization Script**:
    ```bash
    python python/init_infra.py
    ```
    This will execute all SQL scripts in the `sql/` directory in the correct order.

### Method B: Manual Setup (Snowsight)
Copy and paste the contents of the SQL files into a Snowsight Worksheet in this order:
1.  `sql/create_tables.sql`
2.  `sql/load_data.sql` (If you have it)
3.  `sql/dynamic_tables.sql`
4.  `sql/views.sql`
5.  `sql/streams_tasks.sql`
6.  `sql/ai_ml_views.sql`
7.  `sql/unistore.sql` (Enterprise Only)

---

## 💻 Phase 2: Application Deployment

You have two main options for hosting the frontend dashboard.

### ❄️ Option 1: Streamlit in Snowflake (SiS)
*Run the app entirely inside Snowflake's secure boundary.*

1.  **Create the Streamlit Object**:
    ```sql
    CREATE STREAMLIT stockpulse_app
    ROOT_LOCATION = '@stockpulse_db.public.stock_stage'
    MAIN_FILE = '/app.py'
    QUERY_WAREHOUSE = 'COMPUTE_WH';
    ```

2.  **Upload Files**:
    Upload the contents of the `streamlit/` folder to the stage `@stockpulse_db.public.stock_stage`.
    *   `streamlit/app.py` -> `app.py`
    *   `streamlit/pages/` -> `pages/`
    *   `streamlit/styles.py` -> `styles.py`
    *   `streamlit/utils.py` -> `utils.py`

3.  **Handle Dependencies (`environment.yml`)**:
    SiS uses `environment.yml` instead of `requirements.txt`. Create a file named `environment.yml` in the stage:
    ```yaml
    name: stockpulse_env
    channels:
      - snowflake
    dependencies:
      - python=3.8
      - pandas
      - plotly
      - snowflake-snowpark-python
      # streamlit-calendar is not in standard Anaconda channel!
      # You may need to upload the wheel file manually or use pypi fallback if supported in your region.
    ```
    *Note: Custom components like `streamlit-calendar` may require specific package management strategies in SiS (e.g., uploading the `.whl` file to the stage).*

### ☁️ Option 2: Streamlit Community Cloud (Fastest)
*Host for free on Streamlit's cloud, connecting to Snowflake.*

1.  **Push to GitHub**: Ensure your code is in a public GitHub repository.
2.  **Login to Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io).
3.  **New App**:
    *   Repo: `YourName/StockPulse-360`
    *   Main file: `streamlit/app.py`
4.  **Secrets Management**:
    *   Go to App Settings -> Secrets.
    *   Paste the contents of your `.secrets.toml` or `.env` file (User, Password, Account, Warehouse).
    ```toml
    [connections.snowflake]
    user = "..."
    password = "..."
    account = "..."
    role = "ACCOUNTADMIN"
    warehouse = "COMPUTE_WH"
    database = "STOCKPULSE_DB"
    schema = "PUBLIC"
    ```
5.  **Deploy**: Click "Reboot". The app will utilize `requirements.txt` to install `streamlit-calendar` automatically.

---

## 🔄 Phase 3: Automation (Tasks)

Ensure your Tasks are started (they are created in `SUSPENDED` state by default).

```sql
-- Start the master tasks
ALTER TASK process_new_stock RESUME;
ALTER TASK generate_critical_alerts RESUME;
ALTER TASK daily_summary_report RESUME;
```
