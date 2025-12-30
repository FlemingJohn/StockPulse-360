import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SlackNotifier:
    """Sends Slack notifications for stock alerts using Webhooks."""
    
    def __init__(self):
        self.enabled = os.getenv("SLACK_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.channel = os.getenv("SLACK_CHANNEL", "#stock-alerts")
        self.username = os.getenv("SLACK_USERNAME", "StockPulse Bot")
        self.icon = os.getenv("SLACK_ICON", ":hospital:")
        self.mentions = os.getenv("SLACK_MENTION_USERS", "")
    
    def send_alert_message(self, alerts_df: pd.DataFrame):
        """Send a rich Slack message using Blocks API."""
        if not self.enabled:
            return

        if not self.webhook_url:
            print("⚠️ Slack: Webhook URL is missing in .env")
            return
            
        if alerts_df is None or alerts_df.empty:
            print("ℹ️ Slack: No alerts provided.")
            return
            
        # Filter for high priority items
        critical_items = alerts_df[alerts_df['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL', 'WARNING'])]
        if critical_items.empty:
            print(f"ℹ️ Slack: Skipping {len(alerts_df)} alerts (none are OUT_OF_STOCK, CRITICAL, or WARNING).")
            return

        print(f"💬 Preparing Slack message for {len(critical_items)} items...")
        
        # Prepare mention string if exists
        mention_str = ""
        if self.mentions:
            mention_str = " ".join([f"<@{m.strip()}>" for m in self.mentions.split(",")]) + " "

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 StockPulse 360 - Critical Stock Alerts",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{mention_str}*Found {len(critical_items)} items requiring immediate attention.*"
                }
            },
            {"type": "divider"}
        ]
        
        for _, alert in critical_items.iterrows():
            icon = "🔴" if alert['STOCK_STATUS'] == 'OUT_OF_STOCK' else "🟠"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{icon} *{alert['ITEM']}* at *{alert['LOCATION']}*\n"
                            f"• Status: `{alert['STOCK_STATUS']}`\n"
                            f"• Stock Level: `{alert['CURRENT_STOCK']:.0f} units`\n"
                            f"• Est. Stockout: `{alert['DAYS_UNTIL_STOCKOUT']:.1f} days`"
                }
            })
            
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🕒 Reported at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })
        
        self._send(blocks)

    def _send(self, blocks):
        """POST the blocks to Slack Webhook."""
        payload = {
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon,
            "blocks": blocks
        }
        
        try:
            response = requests.post(
                self.webhook_url, 
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                print(f"❌ Slack API Error: {response.text}")
            else:
                print(f"✅ Slack notification delivered to {self.channel}")
        except Exception as e:
            print(f"❌ Failed to reach Slack: {e}")

if __name__ == "__main__":
    # Test script
    test_data = pd.DataFrame([{
        'LOCATION': 'Chennai',
        'ITEM': 'ORS',
        'STOCK_STATUS': 'CRITICAL',
        'CURRENT_STOCK': 50,
        'DAYS_UNTIL_STOCKOUT': 1.5,
        'ALERT_MESSAGE': 'Critical stock at Chennai'
    }])
    notifier = SlackNotifier()
    notifier.send_alert_message(test_data)
