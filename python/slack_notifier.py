"""
StockPulse 360 - Slack Notification System
Sends formatted Slack messages for critical stock situations
"""

import requests
import json
from datetime import datetime
from typing import List, Dict
import pandas as pd

from notification_config import SLACK_CONFIG, NOTIFICATION_RULES, is_quiet_hours


class SlackNotifier:
    """
    Handles Slack notifications for stock alerts.
    Supports rich message formatting with blocks and attachments.
    """
    
    def __init__(self):
        self.config = SLACK_CONFIG
        self.webhook_url = self.config["webhook_url"]
    
    def send_alert_message(self, alerts_df: pd.DataFrame) -> bool:
        """
        Send Slack message with stock alerts.
        
        Args:
            alerts_df: DataFrame with alert data
        
        Returns:
            bool: True if sent successfully
        """
        if not self.config["enabled"]:
            print("⚠️ Slack notifications are disabled")
            return False
        
        if is_quiet_hours():
            print("🔕 Quiet hours - Slack message not sent")
            return False
        
        if alerts_df.empty:
            print("ℹ️ No alerts to send")
            return False
        
        # Filter alerts by configured levels
        alerts_df = alerts_df[
            alerts_df['STOCK_STATUS'].isin(self.config["alert_levels"]) |
            alerts_df['ALERT_TYPE'].isin(self.config["alert_levels"])
        ]
        
        if alerts_df.empty:
            print("ℹ️ No alerts match configured alert levels")
            return False
        
        try:
            # Group alerts if too many
            if NOTIFICATION_RULES["group_alerts"] and \
               len(alerts_df) > NOTIFICATION_RULES["group_threshold"]:
                return self._send_grouped_message(alerts_df)
            else:
                return self._send_detailed_message(alerts_df)
                
        except Exception as e:
            print(f"❌ Failed to send Slack message: {e}")
            return False
    
    def _send_detailed_message(self, alerts_df: pd.DataFrame) -> bool:
        """Send detailed message with individual alert cards."""
        
        # Create message payload
        payload = {
            "username": self.config["username"],
            "icon_emoji": self.config["icon_emoji"],
            "channel": self.config["channel"],
            "blocks": self._create_message_blocks(alerts_df),
            "attachments": self._create_attachments(alerts_df)
        }
        
        # Send to Slack
        response = requests.post(
            self.webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"✅ Slack message sent successfully ({len(alerts_df)} alerts)")
            return True
        else:
            print(f"❌ Slack API error: {response.status_code} - {response.text}")
            return False
    
    def _send_grouped_message(self, alerts_df: pd.DataFrame) -> bool:
        """Send summary message for many alerts."""
        
        # Count by status
        status_counts = alerts_df['STOCK_STATUS'].value_counts().to_dict()
        
        # Create summary payload
        payload = {
            "username": self.config["username"],
            "icon_emoji": self.config["icon_emoji"],
            "channel": self.config["channel"],
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 Stock Alert Summary - {len(alerts_df)} Items Need Attention",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Alerts:*\n{len(alerts_df)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Critical:*\n{status_counts.get('CRITICAL', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Warning:*\n{status_counts.get('WARNING', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Out of Stock:*\n{status_counts.get('OUT_OF_STOCK', 0)}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Top 5 Critical Items:*"
                    }
                }
            ]
        }
        
        # Add top 5 critical items
        top_alerts = alerts_df.head(5)
        for _, alert in top_alerts.iterrows():
            payload["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• *{alert['ITEM']}* at {alert['LOCATION']} - {alert['STOCK_STATUS']}"
                }
            })
        
        # Add action button
        payload["blocks"].append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Full Dashboard",
                        "emoji": True
                    },
                    "url": "https://your-streamlit-app-url.com",
                    "style": "primary"
                }
            ]
        })
        
        # Send to Slack
        response = requests.post(
            self.webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"✅ Slack summary sent successfully ({len(alerts_df)} alerts)")
            return True
        else:
            print(f"❌ Slack API error: {response.status_code} - {response.text}")
            return False
    
    def _create_message_blocks(self, alerts_df: pd.DataFrame) -> List[Dict]:
        """Create Slack message blocks."""
        
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
                    "text": f"*{len(alerts_df)} items* require immediate attention"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add mention for critical alerts
        if self.config["mention_on_critical"] and self.config["mention_users"]:
            critical_count = len(alerts_df[alerts_df['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL'])])
            if critical_count > 0:
                mentions = ' '.join([f"<@{user}>" for user in self.config["mention_users"]])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⚠️ {mentions} - Urgent action required!"
                    }
                })
        
        return blocks
    
    def _create_attachments(self, alerts_df: pd.DataFrame) -> List[Dict]:
        """Create Slack message attachments for each alert."""
        
        attachments = []
        
        for idx, alert in alerts_df.iterrows():
            status = alert.get('STOCK_STATUS', alert.get('ALERT_TYPE', 'UNKNOWN'))
            
            # Color coding
            if status == 'OUT_OF_STOCK':
                color = "#8B0000"
                emoji = "🔴"
            elif status == 'CRITICAL':
                color = "#DC143C"
                emoji = "🟠"
            elif status == 'WARNING':
                color = "#FFA500"
                emoji = "🟡"
            else:
                color = "#FFD700"
                emoji = "ℹ️"
            
            # Create attachment
            attachment = {
                "color": color,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{emoji} *{alert['ITEM']}* at *{alert['LOCATION']}*"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Status:*\n{status}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Current Stock:*\n{alert.get('CURRENT_STOCK', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Avg Daily Usage:*\n{alert.get('AVG_DAILY_USAGE', 'N/A'):.2f}" if pd.notna(alert.get('AVG_DAILY_USAGE')) else "*Avg Daily Usage:*\nN/A"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Days Until Stock-Out:*\n{alert.get('DAYS_UNTIL_STOCKOUT', alert.get('DAYS_LEFT', 'N/A')):.1f}" if pd.notna(alert.get('DAYS_UNTIL_STOCKOUT', alert.get('DAYS_LEFT'))) else "*Days Until Stock-Out:*\nN/A"
                            }
                        ]
                    }
                ]
            }
            
            attachments.append(attachment)
        
        # Add footer
        attachments.append({
            "color": "#36a64f",
            "blocks": [
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Generated by StockPulse 360 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]
        })
        
        return attachments
    
    def send_test_message(self) -> bool:
        """Send a test message to verify configuration."""
        payload = {
            "username": self.config["username"],
            "icon_emoji": self.config["icon_emoji"],
            "channel": self.config["channel"],
            "text": "✅ StockPulse 360 - Slack integration test successful!",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ *StockPulse 360 - Slack Integration Test*\n\nYour Slack notifications are configured correctly!"
                    }
                }
            ]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("✅ Test message sent successfully!")
                return True
            else:
                print(f"❌ Test failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False


# ============================================================================
# Microsoft Teams Notifier (Similar to Slack)
# ============================================================================

class TeamsNotifier:
    """Handles Microsoft Teams notifications."""
    
    def __init__(self):
        from notification_config import TEAMS_CONFIG
        self.config = TEAMS_CONFIG
        self.webhook_url = self.config["webhook_url"]
    
    def send_alert_message(self, alerts_df: pd.DataFrame) -> bool:
        """Send Teams message with stock alerts."""
        
        if not self.config["enabled"]:
            print("⚠️ Teams notifications are disabled")
            return False
        
        if alerts_df.empty:
            return False
        
        # Create Teams adaptive card
        card = self._create_adaptive_card(alerts_df)
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(card),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"✅ Teams message sent successfully ({len(alerts_df)} alerts)")
                return True
            else:
                print(f"❌ Teams API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send Teams message: {e}")
            return False
    
    def _create_adaptive_card(self, alerts_df: pd.DataFrame) -> Dict:
        """Create Teams adaptive card."""
        
        # Create facts for each alert
        facts = []
        for _, alert in alerts_df.head(10).iterrows():  # Limit to 10
            facts.append({
                "title": f"{alert['ITEM']} ({alert['LOCATION']})",
                "value": f"Status: {alert['STOCK_STATUS']} | Stock: {alert.get('CURRENT_STOCK', 'N/A')}"
            })
        
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"StockPulse 360 - {len(alerts_df)} Stock Alerts",
            "themeColor": self.config["theme_color"],
            "title": "🚨 StockPulse 360 - Stock Alerts",
            "sections": [
                {
                    "activityTitle": f"{len(alerts_df)} items require attention",
                    "activitySubtitle": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "facts": facts
                }
            ]
        }
        
        # Add action buttons if enabled
        if self.config["include_action_buttons"]:
            card["potentialAction"] = [
                {
                    "@type": "OpenUri",
                    "name": "View Dashboard",
                    "targets": [
                        {
                            "os": "default",
                            "uri": "https://your-streamlit-app-url.com"
                        }
                    ]
                }
            ]
        
        return card


# ============================================================================
# Test Functions
# ============================================================================

def test_slack_notification():
    """Test Slack notification with sample data."""
    print("=" * 60)
    print("Testing Slack Notification")
    print("=" * 60)
    
    sample_alerts = pd.DataFrame([
        {
            'LOCATION': 'Chennai',
            'ITEM': 'Paracetamol',
            'STOCK_STATUS': 'CRITICAL',
            'CURRENT_STOCK': 50,
            'AVG_DAILY_USAGE': 120,
            'DAYS_UNTIL_STOCKOUT': 0.4
        }
    ])
    
    notifier = SlackNotifier()
    success = notifier.send_alert_message(sample_alerts)
    
    if success:
        print("\n✅ Test Slack message sent!")
    else:
        print("\n❌ Test failed. Check configuration.")


if __name__ == "__main__":
    test_slack_notification()
