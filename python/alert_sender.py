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


class AlertSender:
    """
    Manages alert generation and notification delivery.
    Supports console output, email, and webhook integrations.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.alert_channels = ['console']  # Add 'email', 'slack', 'webhook' as needed
    
    def fetch_critical_alerts(self):
        """
        Fetch all critical and warning alerts from Snowflake.
        """
        print("🔍 Fetching critical alerts...")
        
        alerts_df = self.session.table("critical_alerts").to_pandas()
        
        if alerts_df.empty:
            print("✅ No critical alerts - all stock levels are healthy!")
            return None
        
        print(f"⚠️ Found {len(alerts_df)} alerts")
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
        """
        if alerts_df is None or alerts_df.empty:
            return
        
        print(f"\n📤 Sending {len(alerts_df)} alerts...")
        
        # Always show console alerts
        if 'console' in self.alert_channels:
            self._send_console_alerts(alerts_df)
        
        # Send email notifications
        if 'email' in self.alert_channels:
            try:
                from email_notifier import EmailNotifier
                email_notifier = EmailNotifier()
                email_notifier.send_alert_email(alerts_df)
            except Exception as e:
                print(f"⚠️ Email notification failed: {e}")
        
        # Send Slack notifications
        if 'slack' in self.alert_channels:
            try:
                from slack_notifier import SlackNotifier
                slack_notifier = SlackNotifier()
                slack_notifier.send_alert_message(alerts_df)
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
            status = alert.get('stock_status') or alert.get('alert_type', 'UNKNOWN')
            
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
            print(f"   Location: {alert['location']}")
            print(f"   Item: {alert['item']}")
            print(f"   Status: {status}")
            
            if 'alert_message' in alert:
                print(f"   Message: {alert['alert_message']}")
            
            if 'days_left' in alert and pd.notna(alert['days_left']):
                print(f"   Days Until Stock-Out: {alert['days_left']:.1f}")
            
            if 'current_stock' in alert:
                print(f"   Current Stock: {alert['current_stock']}")
            
            if 'avg_daily_usage' in alert:
                print(f"   Avg Daily Usage: {alert['avg_daily_usage']:.2f}")
            
            if 'recommended_reorder_qty' in alert and pd.notna(alert['recommended_reorder_qty']):
                print(f"   Recommended Reorder: {alert['recommended_reorder_qty']:.0f} units")
        
        print("\n" + "=" * 80)
    
    def get_alert_summary(self):
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


def run_alert_pipeline():
    """
    Main function to run the alert pipeline.
    Can be called from Snowflake Task or run manually.
    """
    print("=" * 60)
    print("StockPulse 360 - Alert Notification Pipeline")
    print("=" * 60)
    
    try:
        # Create session
        session = get_snowflake_session()
        
        # Initialize alert sender
        alert_sender = AlertSender(session)
        
        # Fetch critical alerts
        alerts = alert_sender.fetch_critical_alerts()
        
        if alerts is not None:
            # Send alerts
            alert_sender.send_alerts(alerts)
            
            # Show summary
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
