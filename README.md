# StockPulse 360

**AI-Driven Stock Health Monitor for Hospitals & Public Distribution Systems**

Built with Snowflake for the AI for Good Hackathon 🏆

---

## 🎯 Problem Statement

Hospitals, ration shops, and NGOs struggle with fragmented stock data across multiple systems, leading to:
- ❌ Stock-outs affecting patients and beneficiaries
- ❌ Food and medicine wastage
- ❌ Emergency orders and higher costs
- ❌ Lack of visibility into inventory health

## 💡 Solution

StockPulse 360 provides:
- ✅ **Real-time Stock Health Heatmap** - Visual dashboard showing stock status across locations
- ✅ **AI-Powered Demand Forecasting** - Predict stock-outs 7-14 days in advance
- ✅ **Smart Reorder Recommendations** - Automated procurement suggestions
- ✅ **Critical Alerts** - Instant notifications for low stock situations
- ✅ **One-Click Export** - Ready-to-use procurement lists for teams

---

## 🏗️ Architecture

```
CSV Upload → Snowflake Stage → stock_raw Table
                                      ↓
                            Dynamic Tables (Auto-refresh)
                                      ↓
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
              stock_stats      stock_health    reorder_recommendations
                    ↓                 ↓                 ↓
                    └─────────────────┼─────────────────┘
                                      ↓
                            Views & Streamlit Dashboard
```

---

## 🛠️ Snowflake Technologies Used

| Technology | Purpose |
|------------|---------|
| **SQL Worksheets** | Table creation, data pipelines |
| **Dynamic Tables** | Auto-refresh metrics (usage, safety stock, stock-out dates) |
| **Streams** | Track new stock data insertions |
| **Tasks** | Automate alerts and daily reports |
| **Snowpark (Python)** | AI demand forecasting models |
| **Streamlit** | Interactive dashboard |
| **Unistore** | Store user actions and approvals |

---

## 📁 Project Structure

```
StockPulse 360/
│
├── data/
│   └── stock_data.csv              # Sample stock data
│
├── sql/
│   ├── create_tables.sql           # Base table definitions
│   ├── load_data.sql               # Data ingestion scripts
│   ├── dynamic_tables.sql          # Auto-refresh calculations
│   ├── views.sql                   # Business views
│   └── streams_tasks.sql           # Automation workflows
│
├── python/
│   ├── config.py                   # Snowflake connection config
│   ├── forecast_model.py           # AI demand forecasting
│   ├── alert_sender.py             # Alert notifications
│   └── data_loader.py              # CSV data loader
│
├── streamlit/
│   └── app.py                      # Main dashboard
│
├── requirements.txt                # Python dependencies
├── Project_details.md              # Detailed project documentation
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites

1. **Snowflake Account** - [Sign up for free trial](https://signup.snowflake.com/)
2. **VS Code** with Snowflake extension
3. **Python 3.8+**

### Step 1: Set Up Snowflake

1. Open VS Code and connect to your Snowflake account
2. Run SQL scripts in order:
   ```sql
   -- 1. Create tables and stage
   @sql/create_tables.sql
   
   -- 2. Load sample data
   @sql/load_data.sql
   
   -- 3. Create dynamic tables
   @sql/dynamic_tables.sql
   
   -- 4. Create views
   @sql/views.sql
   
   -- 5. Set up streams and tasks
   @sql/streams_tasks.sql
   ```

### Step 2: Configure Python

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update `python/config.py` with your Snowflake credentials:
   ```python
   SNOWFLAKE_CONFIG = {
       "account": "your_account_identifier",
       "user": "your_username",
       "password": "your_password",
       "warehouse": "compute_wh",
       "database": "stockpulse_db",
       "schema": "public"
   }
   ```

### Step 3: Run Python Modules (Optional)

```bash
# Load data from CSV
python python/data_loader.py

# Generate demand forecasts
python python/forecast_model.py

# Send alerts
python python/alert_sender.py
```

### Step 4: Deploy Streamlit Dashboard

**Option A: Deploy in Snowflake (Recommended)**
1. Go to Snowflake UI → Streamlit
2. Create new Streamlit app
3. Copy contents of `streamlit/app.py`
4. Run the app

**Option B: Run Locally**
```bash
streamlit run streamlit/app.py
```

---

## 📊 Dashboard Features

### 1. **Stock Health Heatmap**
- Color-coded grid (Location × Item)
- 🟢 Green = Healthy | 🟡 Yellow = Warning | 🔴 Red = Critical

### 2. **Critical Alerts**
- Real-time notifications for low stock
- Days until stock-out predictions
- Recommended reorder quantities

### 3. **Location Summary**
- Health score by location
- Status distribution charts
- Overall location performance

### 4. **Procurement Recommendations**
- Auto-generated reorder list
- Priority-based ordering
- One-click CSV export

### 5. **Item Performance**
- Top items by usage
- Demand categorization
- Critical location tracking

---

## 🔄 Automated Workflows

### Tasks (Scheduled Automation)

| Task | Schedule | Purpose |
|------|----------|---------|
| `process_new_stock` | Every 1 hour | Process new stock data |
| `generate_critical_alerts` | Every 30 minutes | Generate alerts for critical items |
| `daily_summary_report` | Daily at 8 AM | Generate daily summary |
| `cleanup_old_alerts` | Weekly (Sunday 2 AM) | Archive old alerts |

### Streams

- `stock_raw_stream` - Tracks new stock insertions
- `stock_health_stream` - Monitors health status changes

---

## 📈 Sample Data

The project includes realistic sample data for:
- **Locations**: Chennai, Mumbai, Delhi
- **Items**: Paracetamol, ORS, Insulin
- **Metrics**: Opening stock, received, issued, closing stock, lead time

---

## 🎯 AI for Good Impact

This solution directly helps:
- 🏥 **Hospitals** - Get early warnings for medicine shortages
- 🍚 **Ration Shops** - Reduce food wastage
- 🤝 **NGOs** - Ensure uninterrupted supplies to beneficiaries
- 👥 **Patients** - Receive timely treatment without stock-outs
- 📊 **Government Teams** - Better planning and resource allocation

---

## 🔗 Snowflake Documentation References

- [Dynamic Tables](https://docs.snowflake.com/en/user-guide/dynamic-tables-intro)
- [Streams](https://docs.snowflake.com/en/user-guide/streams)
- [Tasks](https://docs.snowflake.com/en/user-guide/tasks-intro)
- [Snowpark Python](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

---

## 📝 Next Steps

1. **Enhance Forecasting** - Integrate Snowflake ML models
2. **Add Notifications** - Email/Slack/WhatsApp alerts
3. **Mobile App** - React Native dashboard
4. **Price Integration** - Add cost calculations
5. **Supplier Integration** - Auto-send purchase orders

---

## 👥 Contributing

This is a hackathon project. Feel free to fork and enhance!

---

## 📄 License

MIT License - Built for AI for Good

---

## 🙏 Acknowledgments

- Built with ❄️ Snowflake
- Powered by AI for Good
- Designed for hospitals, NGOs, and public distribution systems

---

**Made with ❤️ for a better world**
