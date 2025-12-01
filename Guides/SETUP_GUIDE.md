# StockPulse 360 - Setup Guide

This guide will walk you through setting up the complete StockPulse 360 project.

---

## 📋 Prerequisites

### 1. Snowflake Account
- Sign up for a [free Snowflake trial](https://signup.snowflake.com/)
- Note your account identifier (e.g., `xy12345.us-east-1`)

### 2. Development Tools
- **VS Code** - [Download](https://code.visualstudio.com/)
- **Snowflake Extension for VS Code** - Install from VS Code marketplace
- **Python 3.8+** - [Download](https://www.python.org/downloads/)

---

## 🔧 Step-by-Step Setup

### Step 1: Snowflake Initial Setup

1. **Login to Snowflake Web UI**
   - Go to your Snowflake account URL
   - Login with your credentials

2. **Create Warehouse**
   ```sql
   CREATE WAREHOUSE IF NOT EXISTS compute_wh
       WAREHOUSE_SIZE = 'XSMALL'
       AUTO_SUSPEND = 300
       AUTO_RESUME = TRUE;
   ```

3. **Set Role**
   ```sql
   USE ROLE ACCOUNTADMIN;
   ```

---

### Step 2: Run SQL Scripts

Open VS Code and connect to Snowflake, then run these scripts in order:

#### 1. Create Tables
```bash
# Open: sql/create_tables.sql
# Execute all statements
```

This creates:
- `stock_raw` - Main stock data table
- `forecast_output` - AI forecast results
- `alert_log` - Alert history
- `user_actions` - User interaction log
- `stock_stage` - File upload stage

#### 2. Load Sample Data

**Option A: Using Snowflake Web UI**
1. Go to Data → Databases → STOCKPULSE_DB → PUBLIC → Stages → STOCK_STAGE
2. Click "Upload Files"
3. Select `data/stock_data.csv`
4. Run the COPY INTO command from `sql/load_data.sql`

**Option B: Using Python**
```bash
python python/data_loader.py
```

#### 3. Create Dynamic Tables
```bash
# Open: sql/dynamic_tables.sql
# Execute all statements
```

This creates auto-refreshing tables:
- `stock_stats` - Usage statistics
- `stock_health` - Health indicators
- `reorder_recommendations` - Procurement suggestions

#### 4. Create Views
```bash
# Open: sql/views.sql
# Execute all statements
```

This creates business views:
- `stock_risk` - Dashboard heatmap data
- `critical_alerts` - Alert notifications
- `procurement_export` - Export-ready recommendations
- `location_summary` - Location-level summaries
- `item_performance` - Item analytics

#### 5. Set Up Automation
```bash
# Open: sql/streams_tasks.sql
# Execute all statements
```

This creates:
- Streams to track data changes
- Tasks for automated processing
- Alert generation workflows

**Important**: Resume tasks after creation:
```sql
ALTER TASK process_new_stock RESUME;
ALTER TASK generate_critical_alerts RESUME;
ALTER TASK daily_summary_report RESUME;
ALTER TASK cleanup_old_alerts RESUME;
```

---

### Step 3: Configure Python Environment

1. **Create Virtual Environment**
   ```bash
   cd "d:\Projects\StockPulse 360"
   python -m venv venv
   ```

2. **Activate Virtual Environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Snowflake Connection**
   
   Edit `python/config.py`:
   ```python
   SNOWFLAKE_CONFIG = {
       "account": "YOUR_ACCOUNT_IDENTIFIER",  # e.g., xy12345.us-east-1
       "user": "YOUR_USERNAME",
       "password": "YOUR_PASSWORD",
       "warehouse": "compute_wh",
       "database": "stockpulse_db",
       "schema": "public",
       "role": "ACCOUNTADMIN"
   }
   ```

   **Security Best Practice**: Use environment variables instead:
   ```bash
   # Windows
   set SNOWFLAKE_ACCOUNT=your_account
   set SNOWFLAKE_USER=your_user
   set SNOWFLAKE_PASSWORD=your_password

   # Mac/Linux
   export SNOWFLAKE_ACCOUNT=your_account
   export SNOWFLAKE_USER=your_user
   export SNOWFLAKE_PASSWORD=your_password
   ```

---

### Step 4: Test Python Modules

1. **Test Data Loader**
   ```bash
   python python/data_loader.py
   ```
   Expected output: ✅ Data loaded successfully

2. **Test Forecast Model**
   ```bash
   python python/forecast_model.py
   ```
   Expected output: ✅ Forecasts generated

3. **Test Alert Sender**
   ```bash
   python python/alert_sender.py
   ```
   Expected output: Alert summary displayed

---

### Step 5: Deploy Streamlit Dashboard

#### Option A: Deploy in Snowflake (Recommended)

1. **Go to Snowflake UI**
   - Navigate to: Projects → Streamlit

2. **Create New Streamlit App**
   - Click "+ Streamlit App"
   - Name: `StockPulse 360 Dashboard`
   - Warehouse: `compute_wh`
   - Database: `stockpulse_db`
   - Schema: `public`

3. **Copy Code**
   - Open `streamlit/app.py`
   - Copy entire contents
   - Paste into Snowflake Streamlit editor

4. **Run**
   - Click "Run"
   - Dashboard should load with data

#### Option B: Run Locally

1. **Run Streamlit**
   ```bash
   streamlit run streamlit/app.py
   ```

2. **Open Browser**
   - Streamlit will open at `http://localhost:8501`

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] All SQL tables created
- [ ] Sample data loaded (27 rows in `stock_raw`)
- [ ] Dynamic tables populated
- [ ] Views return data
- [ ] Tasks are running (check task history)
- [ ] Python modules execute without errors
- [ ] Streamlit dashboard displays data
- [ ] Heatmap shows stock health
- [ ] Alerts are visible
- [ ] Procurement export works

---

## 🔍 Troubleshooting

### Issue: "Table does not exist"
**Solution**: Run `sql/create_tables.sql` first

### Issue: "No data in dashboard"
**Solution**: 
1. Check if data loaded: `SELECT COUNT(*) FROM stock_raw;`
2. If 0, run data loader or COPY INTO command

### Issue: "Dynamic tables not refreshing"
**Solution**: 
1. Check target lag: `SHOW DYNAMIC TABLES;`
2. Manually refresh: `ALTER DYNAMIC TABLE stock_stats REFRESH;`

### Issue: "Tasks not running"
**Solution**:
1. Check task status: `SHOW TASKS;`
2. Resume tasks: `ALTER TASK task_name RESUME;`
3. Check warehouse is running

### Issue: "Python connection failed"
**Solution**:
1. Verify credentials in `config.py`
2. Check account identifier format
3. Ensure warehouse is running
4. Test with: `python -c "from config import get_snowflake_session; get_snowflake_session()"`

---

## 📚 Next Steps

Once setup is complete:

1. **Explore the Dashboard**
   - View stock health heatmap
   - Check critical alerts
   - Download procurement recommendations

2. **Add More Data**
   - Create additional CSV files
   - Upload to stage
   - Run COPY INTO command

3. **Customize**
   - Modify forecast models
   - Add email/Slack notifications
   - Adjust alert thresholds

4. **Schedule Regular Updates**
   - Tasks run automatically
   - Monitor task history
   - Adjust schedules as needed

---

## 🆘 Getting Help

- **Snowflake Docs**: https://docs.snowflake.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Project Issues**: Check `Project_details.md` for detailed information

---

**Setup complete! 🎉 Your StockPulse 360 system is ready to monitor stock health.**
