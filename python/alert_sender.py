"""
StockPulse 360 - Alert Sender
Sends notifications for critical stock situations
Reference: https://docs.snowflake.com/en/developer-guide/snowpark/python/working-with-dataframes
"""

import sys
from datetime import datetime
import pandas as pd
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from config import get_snowflake_session
import argparse


class AlertSender:
    """
    Manages alert generation and notification delivery.
    Supports console output, email, and webhook integrations.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self._load_config()
    
    def _load_config(self):
        """Load notification config from environment."""
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        self.alert_channels = ['console']
        if os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true":
            self.alert_channels.append('email')
        if os.getenv("SLACK_NOTIFICATIONS_ENABLED", "false").lower() == "true":
            self.alert_channels.append('slack')
        
        print(f"📡 Alert Sender initialized with channels: {', '.join(self.alert_channels)}")
    
    def fetch_critical_alerts(self):
        """
        Fetch all critical and warning alerts from Snowflake.
        """
        print("🔍 Fetching critical alerts...")
        
        # Use uppercase column names to match Snowflake table exactly
        alerts_df = self.session.table("critical_alerts").to_pandas()
        
        if alerts_df.empty:
            print("✅ No critical alerts - all stock levels are healthy!")
            return None
        
        print(f"⚠️ Found {len(alerts_df)} active alerts")
        return alerts_df
    
    def fetch_unacknowledged_alerts(self):
        """
        Fetch alerts that haven't been acknowledged yet.
        """
        print("🔍 Fetching unacknowledged alerts...")
        
        alerts_df = self.session.sql("""
            SELECT
                alert_id,
                location,
                item,
                alert_type,
                alert_message,
                days_left,
                recommended_reorder_qty,
                alert_date
            FROM alert_log
            WHERE acknowledged = FALSE
            ORDER BY 
                CASE alert_type
                    WHEN 'OUT_OF_STOCK' THEN 1
                    WHEN 'CRITICAL' THEN 2
                    WHEN 'WARNING' THEN 3
                    ELSE 4
                END,
                alert_date DESC
        """).to_pandas()
        
        if alerts_df.empty:
            print("✅ No unacknowledged alerts")
            return None
        
        print(f"📬 Found {len(alerts_df)} unacknowledged alerts")
        return alerts_df
    
    def send_alerts(self, alerts_df: pd.DataFrame):
        """
        Send alerts through configured channels.
        Filters for OUT_OF_STOCK and CRITICAL statuses for Email and Slack.
        """
        if alerts_df is None or alerts_df.empty:
            return
        
        # High priority items for external notifications
        critical_mask = alerts_df['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL', 'WARNING'])
        critical_alerts = alerts_df[critical_mask]

        print(f"\n📤 Processing {len(alerts_df)} alerts ({len(critical_alerts)} high priority)...")
        
        # 1. Console Output (All alerts)
        if 'console' in self.alert_channels:
            self._send_console_alerts(alerts_df)
        
        # 2. Email Notifications (Critical only)
        if 'email' in self.alert_channels and not critical_alerts.empty:
            try:
                from email_notifier import EmailNotifier
                EmailNotifier().send_alert_email(critical_alerts)
            except Exception as e:
                print(f"⚠️ Email notification failed: {e}")
        
        # 3. Slack Notifications (Critical only)
        if 'slack' in self.alert_channels and not critical_alerts.empty:
            try:
                from slack_notifier import SlackNotifier
                SlackNotifier().send_alert_message(critical_alerts)
            except Exception as e:
                print(f"⚠️ Slack notification failed: {e}")
        
    
    def configure_channels(self, channels: list):
        """
        Configure which notification channels to use.
        
        Args:
            channels: List of channel names ('console', 'email', 'slack')
        """
        valid_channels = ['console', 'email', 'slack']
        self.alert_channels = [ch for ch in channels if ch in valid_channels]
        print(f"✅ Configured channels: {', '.join(self.alert_channels)}")

    
    def _send_console_alerts(self, alerts_df: pd.DataFrame):
        """
        Print alerts to console with color coding.
        """
        print("\n" + "=" * 80)
        print("🚨 STOCKPULSE 360 - CRITICAL ALERTS")
        print("=" * 80)
        
        for idx, alert in alerts_df.iterrows():
            # Standardize status key (View usually has STOCK_STATUS)
            status = alert.get('STOCK_STATUS') or alert.get('ALERT_TYPE', 'UNKNOWN')
            
            # Color coding
            if status == 'OUT_OF_STOCK':
                icon = "🔴"
            elif status == 'CRITICAL':
                icon = "🟠"
            elif status == 'WARNING':
                icon = "🟡"
            else:
                icon = "ℹ️"
            
            print(f"\n{icon} Alert #{idx + 1}")
            print(f"   Location: {alert.get('LOCATION', 'N/A')}")
            print(f"   Item: {alert.get('ITEM', 'N/A')}")
            print(f"   Status: {status}")
            
            if 'ALERT_MESSAGE' in alert:
                print(f"   Message: {alert['ALERT_MESSAGE']}")
            
            # Use DAYS_UNTIL_STOCKOUT to match view schema
            days_left = alert.get('DAYS_UNTIL_STOCKOUT') or alert.get('DAYS_LEFT')
            if pd.notna(days_left):
                print(f"   Days Until Stock-Out: {float(days_left):.1f}")
            
            if 'CURRENT_STOCK' in alert:
                print(f"   Current Stock: {alert['CURRENT_STOCK']}")
            
            if 'AVG_DAILY_USAGE' in alert:
                print(f"   Avg Daily Usage: {alert['AVG_DAILY_USAGE']:.2f}")
            
            # Use REORDER_QUANTITY to match view schema
            reorder_qty = alert.get('REORDER_QUANTITY') or alert.get('RECOMMENDED_REORDER_QTY')
            if pd.notna(reorder_qty):
                print(f"   Recommended Reorder: {float(reorder_qty):.0f} units")
        
        print("\n" + "=" * 80)
    
    def acknowledge_alert(self, alert_id, acknowledged_by="System"):
        """
        Mark an alert as acknowledged.
        """
        try:
            self.session.sql(f"""
                UPDATE alert_log
                SET 
                    acknowledged = TRUE,
                    acknowledged_by = '{acknowledged_by}',
                    acknowledged_at = CURRENT_TIMESTAMP()
                WHERE alert_id = {alert_id}
            """).collect()
            
            print(f"✅ Alert {alert_id} acknowledged by {acknowledged_by}")
            
        except Exception as e:
            print(f"❌ Error acknowledging alert: {e}")
    
    def get_alert_summary(self):
        """
        Get summary statistics of alerts.
        """
        summary_df = self.session.sql("""
            SELECT
                alert_type,
                COUNT(*) as count,
                SUM(CASE WHEN acknowledged THEN 1 ELSE 0 END) as acknowledged_count,
                SUM(CASE WHEN acknowledged THEN 0 ELSE 1 END) as pending_count
            FROM alert_log
            WHERE alert_date >= DATEADD(day, -7, CURRENT_DATE())
            GROUP BY alert_type
            ORDER BY count DESC
        """).to_pandas()
        
        return summary_df


        return summary_df


def run_alert_pipeline():
    """
    Main function to run the alert pipeline.
    Modes:
    - immediate: Checks only for OUT_OF_STOCK (run frequently)
    - daily: Checks for CRITICAL/WARNING (run daily morning)
    - all: Checks everything (default)
    """
    parser = argparse.ArgumentParser(description='StockPulse 360 Alert Sender')
    parser.add_argument('--mode', choices=['immediate', 'daily', 'all'], default='all',
                        help='Alert mode: immediate (SOS only), daily (Morning Report), or all')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"StockPulse 360 - Alert Notification Pipeline (Mode: {args.mode})")
    print("=" * 60)
    
    try:
        # Create session
        session = get_snowflake_session()
        
        # Initialize alert sender
        alert_sender = AlertSender(session)
        
        # Fetch critical alerts
        alerts = alert_sender.fetch_critical_alerts()
        
        if alerts is not None:
            # Filter based on mode
            if args.mode == 'immediate':
                # Only OUT_OF_STOCK
                filtered_alerts = alerts[alerts['STOCK_STATUS'] == 'OUT_OF_STOCK']
                if not filtered_alerts.empty:
                    print(f"⚡ IMMEDIATE MODE: Sending {len(filtered_alerts)} OUT_OF_STOCK alerts")
                    alert_sender.send_alerts(filtered_alerts)
                else:
                    print("✅ No OUT_OF_STOCK items found for immediate alert.")
                    
            elif args.mode == 'daily':
                # Warnings and Critical (Morning Report)
                # We exclude OUT_OF_STOCK if handled by immediate, or include everything?
                # Usually daily report includes everything for full context.
                print(f"🌅 DAILY MODE: Processing Morning Report for {len(alerts)} items")
                alert_sender.send_alerts(alerts)
                
            else:
                # 'all' mode - standard behavior
                alert_sender.send_alerts(alerts)
            
            # Show summary (always useful)
            print("\n📊 Alert Summary (Last 7 Days):")
            summary = alert_sender.get_alert_summary()
            if not summary.empty:
                print(summary.to_string(index=False))
        
        # Close session
        session.close()
        print("\n✅ Alert pipeline completed successfully")
        
    except Exception as e:
        print(f"\n❌ Alert pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_alert_pipeline()
