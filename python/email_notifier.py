"""
StockPulse 360 - Email Notification System
Sends formatted email alerts for critical stock situations
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
import pandas as pd

from notification_config import EMAIL_CONFIG, NOTIFICATION_RULES, is_quiet_hours


class EmailNotifier:
    """
    Handles email notifications for stock alerts.
    Supports HTML emails with formatted tables and styling.
    """
    
    def __init__(self):
        self.config = EMAIL_CONFIG
        self.smtp_connection = None
    
    def connect(self):
        """Establish SMTP connection."""
        try:
            if self.config["use_tls"]:
                self.smtp_connection = smtplib.SMTP(
                    self.config["smtp_host"],
                    self.config["smtp_port"]
                )
                self.smtp_connection.starttls()
            else:
                self.smtp_connection = smtplib.SMTP_SSL(
                    self.config["smtp_host"],
                    self.config["smtp_port"]
                )
            
            self.smtp_connection.login(
                self.config["smtp_user"],
                self.config["smtp_password"]
            )
            
            print("✅ Connected to SMTP server")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to SMTP server: {e}")
            return False
    
    def disconnect(self):
        """Close SMTP connection."""
        if self.smtp_connection:
            self.smtp_connection.quit()
            print("📪 Disconnected from SMTP server")
    
    def send_alert_email(self, alerts_df: pd.DataFrame) -> bool:
        """
        Send email with stock alerts.
        
        Args:
            alerts_df: DataFrame with alert data
        
        Returns:
            bool: True if sent successfully
        """
        if not self.config["enabled"]:
            print("⚠️ Email notifications are disabled")
            return False
        
        if is_quiet_hours():
            print("🔕 Quiet hours - email not sent")
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
            # Connect to SMTP
            if not self.connect():
                return False
            
            # Create email
            msg = self._create_email_message(alerts_df)
            
            # Send to all recipients
            recipients = self.config["to_emails"] + self.config["cc_emails"]
            recipients = [email.strip() for email in recipients if email.strip()]
            
            self.smtp_connection.send_message(msg)
            
            print(f"✅ Email sent to {len(recipients)} recipients")
            print(f"   Recipients: {', '.join(recipients)}")
            
            self.disconnect()
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            if self.smtp_connection:
                self.disconnect()
            return False
    
    def _create_email_message(self, alerts_df: pd.DataFrame) -> MIMEMultipart:
        """Create formatted email message."""
        msg = MIMEMultipart('alternative')
        
        # Email headers
        msg['Subject'] = self._create_subject(alerts_df)
        msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
        msg['To'] = ', '.join(self.config["to_emails"])
        if self.config["cc_emails"]:
            msg['Cc'] = ', '.join(self.config["cc_emails"])
        
        # Create plain text version
        text_content = self._create_text_content(alerts_df)
        text_part = MIMEText(text_content, 'plain')
        
        # Create HTML version
        html_content = self._create_html_content(alerts_df)
        html_part = MIMEText(html_content, 'html')
        
        # Attach both versions (email clients will choose)
        msg.attach(text_part)
        msg.attach(html_part)
        
        return msg
    
    def _create_subject(self, alerts_df: pd.DataFrame) -> str:
        """Create email subject line."""
        critical_count = len(alerts_df[alerts_df['STOCK_STATUS'] == 'CRITICAL'])
        out_of_stock_count = len(alerts_df[alerts_df['STOCK_STATUS'] == 'OUT_OF_STOCK'])
        
        if out_of_stock_count > 0:
            return f"🚨 URGENT: {out_of_stock_count} Items Out of Stock - StockPulse 360"
        elif critical_count > 0:
            return f"⚠️ CRITICAL: {critical_count} Stock Alerts - StockPulse 360"
        else:
            return f"📊 Stock Alert: {len(alerts_df)} Items Need Attention - StockPulse 360"
    
    def _create_text_content(self, alerts_df: pd.DataFrame) -> str:
        """Create plain text email content."""
        content = f"""
StockPulse 360 - Stock Alert Notification
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 60}
CRITICAL STOCK ALERTS
{'=' * 60}

Total Alerts: {len(alerts_df)}

"""
        for idx, alert in alerts_df.iterrows():
            content += f"""
Alert #{idx + 1}
Status: {alert.get('STOCK_STATUS', alert.get('ALERT_TYPE', 'UNKNOWN'))}
Location: {alert['LOCATION']}
Item: {alert['ITEM']}
Current Stock: {alert.get('CURRENT_STOCK', 'N/A')}
Avg Daily Usage: {alert.get('AVG_DAILY_USAGE', 'N/A')}
Days Until Stock-Out: {alert.get('DAYS_UNTIL_STOCKOUT', alert.get('DAYS_LEFT', 'N/A'))}
{'-' * 60}
"""
        
        content += f"""

ACTION REQUIRED:
Please review the stock levels and place orders as needed.

---
This is an automated message from StockPulse 360.
"""
        return content
    
    def _create_html_content(self, alerts_df: pd.DataFrame) -> str:
        """Create HTML email content with styling."""
        
        # Count alerts by severity
        critical_count = len(alerts_df[alerts_df['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL'])])
        warning_count = len(alerts_df[alerts_df['STOCK_STATUS'] == 'WARNING'])
        
        # Create alert rows
        alert_rows = ""
        for idx, alert in alerts_df.iterrows():
            status = alert.get('STOCK_STATUS', alert.get('ALERT_TYPE', 'UNKNOWN'))
            
            # Color coding
            if status == 'OUT_OF_STOCK':
                bg_color = '#8B0000'
                text_color = '#FFFFFF'
            elif status == 'CRITICAL':
                bg_color = '#DC143C'
                text_color = '#FFFFFF'
            elif status == 'WARNING':
                bg_color = '#FFA500'
                text_color = '#000000'
            else:
                bg_color = '#FFD700'
                text_color = '#000000'
            
            alert_rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">{alert['LOCATION']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>{alert['ITEM']}</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; background-color: {bg_color}; color: {text_color}; font-weight: bold; text-align: center;">{status}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">{alert.get('CURRENT_STOCK', 'N/A')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">{alert.get('AVG_DAILY_USAGE', 'N/A')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">{alert.get('DAYS_UNTIL_STOCKOUT', alert.get('DAYS_LEFT', 'N/A'))}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px;">📊 StockPulse 360</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Stock Alert Notification</p>
            </div>
            
            <!-- Summary Cards -->
            <div style="display: flex; gap: 15px; margin-bottom: 30px;">
                <div style="flex: 1; background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h3 style="margin: 0 0 10px 0; color: #856404;">Total Alerts</h3>
                    <p style="margin: 0; font-size: 32px; font-weight: bold; color: #856404;">{len(alerts_df)}</p>
                </div>
                <div style="flex: 1; background: #f8d7da; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
                    <h3 style="margin: 0 0 10px 0; color: #721c24;">Critical</h3>
                    <p style="margin: 0; font-size: 32px; font-weight: bold; color: #721c24;">{critical_count}</p>
                </div>
                <div style="flex: 1; background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h3 style="margin: 0 0 10px 0; color: #856404;">Warning</h3>
                    <p style="margin: 0; font-size: 32px; font-weight: bold; color: #856404;">{warning_count}</p>
                </div>
            </div>
            
            <!-- Alert Table -->
            <div style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Location</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Item</th>
                            <th style="padding: 12px; text-align: center; border-bottom: 2px solid #dee2e6;">Status</th>
                            <th style="padding: 12px; text-align: right; border-bottom: 2px solid #dee2e6;">Current Stock</th>
                            <th style="padding: 12px; text-align: right; border-bottom: 2px solid #dee2e6;">Avg Daily Usage</th>
                            <th style="padding: 12px; text-align: right; border-bottom: 2px solid #dee2e6;">Days Left</th>
                        </tr>
                    </thead>
                    <tbody>
                        {alert_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Action Required -->
            <div style="background: #d1ecf1; border: 1px solid #bee5eb; border-radius: 8px; padding: 20px; margin-bottom: 30px;">
                <h3 style="margin: 0 0 10px 0; color: #0c5460;">⚡ Action Required</h3>
                <p style="margin: 0; color: #0c5460;">Please review the stock levels above and place orders as needed to prevent stock-outs.</p>
            </div>
            
            <!-- Footer -->
            <div style="text-align: center; color: #6c757d; font-size: 14px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>This is an automated message from <strong>StockPulse 360</strong></p>
                <p style="margin: 10px 0 0 0;">Powered by Snowflake ❄️</p>
            </div>
            
        </body>
        </html>
        """
        
        return html


# ============================================================================
# Standalone Test Function
# ============================================================================

def test_email_notification():
    """Test email notification with sample data."""
    print("=" * 60)
    print("Testing Email Notification")
    print("=" * 60)
    
    # Create sample alert data
    sample_alerts = pd.DataFrame([
        {
            'LOCATION': 'Chennai',
            'ITEM': 'Paracetamol',
            'STOCK_STATUS': 'CRITICAL',
            'CURRENT_STOCK': 50,
            'AVG_DAILY_USAGE': 120,
            'DAYS_UNTIL_STOCKOUT': 0.4
        },
        {
            'LOCATION': 'Mumbai',
            'ITEM': 'ORS',
            'STOCK_STATUS': 'WARNING',
            'CURRENT_STOCK': 150,
            'AVG_DAILY_USAGE': 100,
            'DAYS_UNTIL_STOCKOUT': 1.5
        }
    ])
    
    # Send email
    notifier = EmailNotifier()
    success = notifier.send_alert_email(sample_alerts)
    
    if success:
        print("\n✅ Test email sent successfully!")
    else:
        print("\n❌ Test email failed. Check configuration.")


if __name__ == "__main__":
    test_email_notification()
