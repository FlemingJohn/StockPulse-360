# StockPulse 360 - Snowflake Configuration Examples

This file contains example configurations for different Snowflake setups.

---

## Method 1: Direct Configuration (Development Only)

Edit `python/config.py`:

```python
SNOWFLAKE_CONFIG = {
    "account": "xy12345.us-east-1",  # Your account identifier
    "user": "your_username",
    "password": "your_password",
    "warehouse": "compute_wh",
    "database": "stockpulse_db",
    "schema": "public",
    "role": "ACCOUNTADMIN"
}
```

⚠️ **Warning**: Never commit passwords to version control!

---

## Method 2: Environment Variables (Recommended)

### Windows (PowerShell)
```powershell
$env:SNOWFLAKE_ACCOUNT = "xy12345.us-east-1"
$env:SNOWFLAKE_USER = "your_username"
$env:SNOWFLAKE_PASSWORD = "your_password"
$env:SNOWFLAKE_WAREHOUSE = "compute_wh"
$env:SNOWFLAKE_DATABASE = "stockpulse_db"
$env:SNOWFLAKE_SCHEMA = "public"
```

### Windows (Command Prompt)
```cmd
set SNOWFLAKE_ACCOUNT=xy12345.us-east-1
set SNOWFLAKE_USER=your_username
set SNOWFLAKE_PASSWORD=your_password
set SNOWFLAKE_WAREHOUSE=compute_wh
set SNOWFLAKE_DATABASE=stockpulse_db
set SNOWFLAKE_SCHEMA=public
```

### Mac/Linux (Bash)
```bash
export SNOWFLAKE_ACCOUNT="xy12345.us-east-1"
export SNOWFLAKE_USER="your_username"
export SNOWFLAKE_PASSWORD="your_password"
export SNOWFLAKE_WAREHOUSE="compute_wh"
export SNOWFLAKE_DATABASE="stockpulse_db"
export SNOWFLAKE_SCHEMA="public"
```

---

## Method 3: .env File (Best for Local Development)

1. Create `.env` file in project root:
```env
SNOWFLAKE_ACCOUNT=xy12345.us-east-1
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=compute_wh
SNOWFLAKE_DATABASE=stockpulse_db
SNOWFLAKE_SCHEMA=public
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

2. Install python-dotenv:
```bash
pip install python-dotenv
```

3. Update `python/config.py`:
```python
from dotenv import load_dotenv
load_dotenv()

SNOWFLAKE_CONFIG = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
}
```

---

## Method 4: Snowflake Config File

1. Create `~/.snowflake/config`:

**Windows**: `C:\Users\YourUsername\.snowflake\config`
**Mac/Linux**: `~/.snowflake/config`

2. Add connection details:
```ini
[connections.stockpulse]
account = xy12345.us-east-1
user = your_username
password = your_password
warehouse = compute_wh
database = stockpulse_db
schema = public
role = ACCOUNTADMIN
```

3. Use in Python:
```python
from snowflake.snowpark import Session

session = Session.builder.config_file("~/.snowflake/config", "stockpulse").create()
```

---

## Finding Your Account Identifier

### Method 1: From Snowflake URL
Your Snowflake URL looks like:
```
https://xy12345.us-east-1.snowflakecomputing.com
```

Your account identifier is: `xy12345.us-east-1`

### Method 2: From Snowflake UI
1. Login to Snowflake
2. Click your username (bottom left)
3. Hover over account name
4. Copy the account identifier

### Method 3: Using SQL
```sql
SELECT CURRENT_ACCOUNT();
SELECT CURRENT_REGION();
```

Combine as: `ACCOUNT.REGION`

---

## Warehouse Configuration

### Create Warehouse (if not exists)
```sql
CREATE WAREHOUSE IF NOT EXISTS compute_wh
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;
```

### Warehouse Sizes
- `XSMALL` - Good for development/testing
- `SMALL` - Light production workloads
- `MEDIUM` - Moderate workloads
- `LARGE` - Heavy workloads

---

## Security Best Practices

1. ✅ **Use environment variables** for credentials
2. ✅ **Add `.env` to `.gitignore`**
3. ✅ **Use role-based access control**
4. ✅ **Enable MFA** on your Snowflake account
5. ✅ **Rotate passwords** regularly
6. ❌ **Never commit passwords** to version control
7. ❌ **Never share credentials** in chat/email

---

## Troubleshooting

### Error: "Invalid account identifier"
- Check format: `account.region` (e.g., `xy12345.us-east-1`)
- Don't include `https://` or `.snowflakecomputing.com`

### Error: "Incorrect username or password"
- Verify credentials in Snowflake UI
- Check for typos
- Ensure account is not locked

### Error: "Warehouse does not exist"
- Create warehouse using SQL above
- Or use existing warehouse name

### Error: "Database does not exist"
- Run `sql/create_tables.sql` first
- Or change database name in config

---

## Testing Connection

Run this to test your connection:

```python
from config import get_snowflake_session

try:
    session = get_snowflake_session()
    result = session.sql("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE()").collect()
    print("✅ Connection successful!")
    print(result)
    session.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

---

**Keep your credentials secure! 🔒**
