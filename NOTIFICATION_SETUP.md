# StockPulse 360 - Notification Setup Guide

This guide explains how to configure email and Slack/Teams notifications for StockPulse 360.

---

## 📧 Email Notifications

### Step 1: Get SMTP Credentials

#### Option A: Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other" → Enter "StockPulse 360"
   - Copy the 16-character password

3. **Configure Environment Variables**:

**Windows (PowerShell):**
```powershell
$env:EMAIL_NOTIFICATIONS_ENABLED = "true"
$env:SMTP_HOST = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SMTP_USER = "your-email@gmail.com"
$env:SMTP_PASSWORD = "your-16-char-app-password"
$env:EMAIL_FROM = "stockpulse@hospital.com"
$env:EMAIL_TO = "procurement@hospital.com,admin@hospital.com"
```

**Mac/Linux (Bash):**
```bash
export EMAIL_NOTIFICATIONS_ENABLED="true"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-16-char-app-password"
export EMAIL_FROM="stockpulse@hospital.com"
export EMAIL_TO="procurement@hospital.com,admin@hospital.com"
```

#### Option B: Other Email Providers

**Outlook/Office 365:**
```
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
```

**Yahoo:**
```
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
```

**SendGrid (Production):**
```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### Step 2: Test Email Configuration

```python
python python/email_notifier.py
```

Expected output:
```
✅ Connected to SMTP server
✅ Email sent to 2 recipients
   Recipients: procurement@hospital.com, admin@hospital.com
📪 Disconnected from SMTP server
✅ Test email sent successfully!
```

---

## 💬 Slack Notifications

### Step 1: Create Slack Webhook

1. **Go to Slack App Directory**:
   - Visit: https://api.slack.com/messaging/webhooks

2. **Create Incoming Webhook**:
   - Click "Create New App" → "From scratch"
   - App Name: "StockPulse 360"
   - Select your workspace
   - Click "Incoming Webhooks" → Toggle ON
   - Click "Add New Webhook to Workspace"
   - Select channel (e.g., #stock-alerts)
   - Copy the Webhook URL

3. **Configure Environment Variables**:

**Windows:**
```powershell
$env:SLACK_NOTIFICATIONS_ENABLED = "true"
$env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
$env:SLACK_CHANNEL = "#stock-alerts"
```

**Mac/Linux:**
```bash
export SLACK_NOTIFICATIONS_ENABLED="true"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
export SLACK_CHANNEL="#stock-alerts"
```

### Step 2: Test Slack Configuration

```python
python python/slack_notifier.py
```

Expected output:
```
✅ Slack message sent successfully (1 alerts)
✅ Test Slack message sent!
```

### Step 3: Advanced Slack Features

**Mention Users on Critical Alerts:**
```powershell
$env:SLACK_MENTION_USERS = "U12345678,U87654321"  # User IDs
```

To get User IDs:
- Click user profile in Slack → "..." → "Copy member ID"

---

## 👥 Microsoft Teams Notifications

### Step 1: Create Teams Webhook

1. **Open Teams Channel**:
   - Go to the channel where you want alerts
   - Click "..." → "Connectors"

2. **Configure Incoming Webhook**:
   - Search for "Incoming Webhook"
   - Click "Configure"
   - Name: "StockPulse 360"
   - Upload icon (optional)
   - Click "Create"
   - Copy the Webhook URL

3. **Configure Environment Variables**:

```powershell
$env:TEAMS_NOTIFICATIONS_ENABLED = "true"
$env:TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/..."
```

---

## 🔧 Using .env File (Recommended)

Create a `.env` file in the project root:

```env
# Email Configuration
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=stockpulse@hospital.com
EMAIL_TO=procurement@hospital.com,admin@hospital.com

# Slack Configuration
SLACK_NOTIFICATIONS_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#stock-alerts
SLACK_USERNAME=StockPulse Bot
SLACK_MENTION_USERS=U12345678

# Teams Configuration
TEAMS_NOTIFICATIONS_ENABLED=true
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/YOUR/WEBHOOK/URL

# Notification Rules
QUIET_HOURS_ENABLED=false
QUIET_HOURS_START=22
QUIET_HOURS_END=7
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

---

## 🎯 Integration with Alert Sender

Update `alert_sender.py` to use notifications:

```python
from alert_sender import AlertSender

# Configure channels
alert_sender = AlertSender(session)
alert_sender.configure_channels(['console', 'email', 'slack'])

# Fetch and send alerts
alerts = alert_sender.fetch_critical_alerts()
alert_sender.send_alerts(alerts)
```

---

## 📋 Notification Configuration Options

### Alert Levels

Configure which alert levels trigger notifications:

```python
# In notification_config.py

EMAIL_CONFIG = {
    "alert_levels": ["OUT_OF_STOCK", "CRITICAL"],  # Only critical
}

SLACK_CONFIG = {
    "alert_levels": ["OUT_OF_STOCK", "CRITICAL", "WARNING"],  # More alerts
}
```

### Quiet Hours

Prevent notifications during night hours:

```python
NOTIFICATION_RULES = {
    "quiet_hours_enabled": True,
    "quiet_hours_start": 22,  # 10 PM
    "quiet_hours_end": 7,     # 7 AM
}
```

### Rate Limiting

Prevent notification spam:

```python
NOTIFICATION_RULES = {
    "rate_limit_enabled": True,
    "max_alerts_per_hour": 10,
    "max_alerts_per_day": 50,
}
```

### Alert Grouping

Combine multiple alerts into one message:

```python
NOTIFICATION_RULES = {
    "group_alerts": True,
    "group_threshold": 5,  # Group if more than 5 alerts
}
```

---

## 🧪 Testing Notifications

### Test All Channels

```python
# Run from project root
python -c "
from python.notification_config import validate_config, get_active_channels
print('Active Channels:', get_active_channels())
print('Validation:', validate_config())
"
```

### Test Individual Channels

**Email:**
```bash
python python/email_notifier.py
```

**Slack:**
```bash
python python/slack_notifier.py
```

### Test from Alert Sender

```python
python python/alert_sender.py
```

---

## 🔒 Security Best Practices

1. ✅ **Never commit credentials** to version control
2. ✅ **Use environment variables** or `.env` file
3. ✅ **Add `.env` to `.gitignore`**
4. ✅ **Use app passwords** instead of account passwords
5. ✅ **Rotate credentials** regularly
6. ✅ **Limit webhook access** to specific channels
7. ✅ **Enable rate limiting** to prevent abuse

---

## 🚀 Production Deployment

### Snowflake Task Integration

Update `sql/streams_tasks.sql` to include notifications:

```sql
CREATE OR REPLACE TASK generate_critical_alerts
    WAREHOUSE = compute_wh
    SCHEDULE = '30 MINUTE'
AS
BEGIN
    -- Generate alerts
    INSERT INTO alert_log (...) SELECT ...;
    
    -- Trigger Python notification script
    CALL SYSTEM$SEND_EMAIL(
        'procurement@hospital.com',
        'StockPulse Alert',
        'Critical stock levels detected'
    );
END;
```

### Snowpark Stored Procedure

```python
# Create stored procedure for notifications
from snowflake.snowpark import Session

def send_notifications(session: Session):
    from alert_sender import AlertSender
    
    alert_sender = AlertSender(session)
    alert_sender.configure_channels(['email', 'slack'])
    
    alerts = alert_sender.fetch_critical_alerts()
    alert_sender.send_alerts(alerts)
    
    return "Notifications sent"

# Register as stored procedure
session.sproc.register(
    func=send_notifications,
    name="send_stock_alerts",
    packages=["snowflake-snowpark-python"]
)
```

---

## 📊 Monitoring Notifications

Check notification delivery:

```sql
-- View recent user actions (notification logs)
SELECT 
    action_type,
    action_data,
    action_timestamp
FROM user_actions
WHERE action_type IN ('EMAIL_SENT', 'SLACK_SENT', 'TEAMS_SENT')
ORDER BY action_timestamp DESC
LIMIT 10;
```

---

## 🆘 Troubleshooting

### Email Issues

**Error: "Authentication failed"**
- Verify SMTP credentials
- Use app password (not account password)
- Check 2FA is enabled

**Error: "Connection timeout"**
- Check SMTP_HOST and SMTP_PORT
- Verify firewall allows outbound SMTP
- Try port 465 (SSL) instead of 587 (TLS)

### Slack Issues

**Error: "Invalid webhook URL"**
- Verify webhook URL is complete
- Check webhook hasn't been deleted in Slack
- Ensure workspace permissions

**Message not appearing:**
- Check channel permissions
- Verify bot is added to channel
- Test with simple message first

### Teams Issues

**Error: "Webhook not found"**
- Recreate webhook in Teams
- Verify connector is still active
- Check channel exists

---

**Notifications are now configured! 🎉**

Test with: `python python/alert_sender.py`
