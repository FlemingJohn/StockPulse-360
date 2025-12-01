"""
StockPulse 360 - Notification Configuration
Centralized configuration for email and Slack/Teams notifications
"""

import os
from typing import List, Dict

# ============================================================================
# Email Configuration (SMTP)
# ============================================================================

EMAIL_CONFIG = {
    "enabled": os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true",
    
    # SMTP Server Settings
    "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    
    # Authentication
    "smtp_user": os.getenv("SMTP_USER", "your-email@gmail.com"),
    "smtp_password": os.getenv("SMTP_PASSWORD", "your-app-password"),
    
    # Email Settings
    "from_email": os.getenv("EMAIL_FROM", "stockpulse@hospital.com"),
    "from_name": os.getenv("EMAIL_FROM_NAME", "StockPulse 360 Alerts"),
    
    # Recipients
    "to_emails": os.getenv("EMAIL_TO", "procurement@hospital.com,admin@hospital.com").split(","),
    "cc_emails": os.getenv("EMAIL_CC", "").split(",") if os.getenv("EMAIL_CC") else [],
    
    # Alert Thresholds (which alerts to send via email)
    "alert_levels": ["OUT_OF_STOCK", "CRITICAL"],  # Only send critical alerts
    
    # Email Template Settings
    "include_logo": True,
    "include_charts": False,  # Set to True to embed charts (requires more setup)
}

# ============================================================================
# Slack Configuration
# ============================================================================

SLACK_CONFIG = {
    "enabled": os.getenv("SLACK_NOTIFICATIONS_ENABLED", "false").lower() == "true",
    
    # Webhook URL (Get from Slack: https://api.slack.com/messaging/webhooks)
    "webhook_url": os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"),
    
    # Channel Settings
    "channel": os.getenv("SLACK_CHANNEL", "#stock-alerts"),
    "username": os.getenv("SLACK_USERNAME", "StockPulse Bot"),
    "icon_emoji": os.getenv("SLACK_ICON", ":hospital:"),
    
    # Alert Thresholds
    "alert_levels": ["OUT_OF_STOCK", "CRITICAL", "WARNING"],
    
    # Mention users for critical alerts
    "mention_users": os.getenv("SLACK_MENTION_USERS", "").split(",") if os.getenv("SLACK_MENTION_USERS") else [],
    "mention_on_critical": True,
}

# ============================================================================
# Notification Rules
# ============================================================================

NOTIFICATION_RULES = {
    # Quiet hours (no notifications during these hours, 24-hour format)
    "quiet_hours_enabled": False,
    "quiet_hours_start": 22,  # 10 PM
    "quiet_hours_end": 7,     # 7 AM
    
    # Rate limiting (prevent spam)
    "rate_limit_enabled": True,
    "max_alerts_per_hour": 10,
    "max_alerts_per_day": 50,
    
    # Deduplication (don't send same alert multiple times)
    "deduplicate_enabled": True,
    "deduplicate_window_hours": 24,
    
    # Alert grouping (combine multiple alerts into one message)
    "group_alerts": True,
    "group_threshold": 5,  # If more than 5 alerts, send as summary
}

# ============================================================================
# Helper Functions
# ============================================================================

def get_active_channels() -> List[str]:
    """Get list of enabled notification channels."""
    channels = []
    if EMAIL_CONFIG["enabled"]:
        channels.append("email")
    if SLACK_CONFIG["enabled"]:
        channels.append("slack")
    return channels

def should_send_notification(alert_level: str, channel: str) -> bool:
    """Check if notification should be sent based on alert level and channel."""
    if channel == "email":
        return alert_level in EMAIL_CONFIG["alert_levels"]
    elif channel == "slack":
        return alert_level in SLACK_CONFIG["alert_levels"]
    return False

def is_quiet_hours() -> bool:
    """Check if current time is within quiet hours."""
    if not NOTIFICATION_RULES["quiet_hours_enabled"]:
        return False
    
    from datetime import datetime
    current_hour = datetime.now().hour
    start = NOTIFICATION_RULES["quiet_hours_start"]
    end = NOTIFICATION_RULES["quiet_hours_end"]
    
    if start < end:
        return start <= current_hour < end
    else:  # Overnight quiet hours
        return current_hour >= start or current_hour < end

# ============================================================================
# Configuration Validation
# ============================================================================

def validate_config() -> Dict[str, bool]:
    """Validate notification configurations."""
    validation = {
        "email": False,
        "slack": False,
    }
    
    # Validate Email
    if EMAIL_CONFIG["enabled"]:
        if EMAIL_CONFIG["smtp_user"] != "your-email@gmail.com" and \
           EMAIL_CONFIG["smtp_password"] != "your-app-password":
            validation["email"] = True
    
    # Validate Slack
    if SLACK_CONFIG["enabled"]:
        if "YOUR/WEBHOOK/URL" not in SLACK_CONFIG["webhook_url"]:
            validation["slack"] = True
    
    return validation

# ============================================================================
# Print Configuration Status
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("StockPulse 360 - Notification Configuration Status")
    print("=" * 60)
    
    active_channels = get_active_channels()
    print(f"\n✅ Active Channels: {', '.join(active_channels) if active_channels else 'None'}")
    
    validation = validate_config()
    print("\n📋 Configuration Validation:")
    for channel, is_valid in validation.items():
        status = "✅ Valid" if is_valid else "⚠️ Not Configured"
        print(f"  {channel.capitalize()}: {status}")
    
    print(f"\n🔕 Quiet Hours: {'Enabled' if NOTIFICATION_RULES['quiet_hours_enabled'] else 'Disabled'}")
    print(f"🚦 Rate Limiting: {'Enabled' if NOTIFICATION_RULES['rate_limit_enabled'] else 'Disabled'}")
    print(f"🔄 Deduplication: {'Enabled' if NOTIFICATION_RULES['deduplicate_enabled'] else 'Disabled'}")
    
    print("\n" + "=" * 60)
