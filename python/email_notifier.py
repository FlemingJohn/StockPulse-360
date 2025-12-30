import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class EmailNotifier:
    """Sends email notifications for stock alerts."""
    
    def __init__(self):
        self.enabled = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        self.host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("EMAIL_FROM")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "StockPulse 360")
        self.to_emails = os.getenv("EMAIL_TO", "").split(",")
    
    def send_alert_email(self, alerts_df: pd.DataFrame):
        """Send formatted HTML email with critical alerts."""
        if not self.enabled:
            return
            
        if alerts_df is None or alerts_df.empty:
            print("ℹ️ Email: No alerts provided.")
            return
            
        # Filter for high priority items
        critical_items = alerts_df[alerts_df['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL', 'WARNING'])]
        if critical_items.empty:
            print(f"ℹ️ Email: Skipping {len(alerts_df)} alerts (none are OUT_OF_STOCK, CRITICAL, or WARNING).")
            return

        print(f"📧 Preparing email for {len(critical_items)} critical items...")
        
        subject = f"🚨 URGENT: {len(critical_items)} Critical Stock Alerts - StockPulse 360"
        
        # Build HTML content
        html = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="background-color: #0F4C81; color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">❄️ StockPulse 360 Alerts</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.8;">Critical Inventory Notification</p>
            </div>
            <div style="padding: 20px; border: 1px solid #E0E0E0; border-radius: 0 0 10px 10px;">
                <p>The following items have reached <b>Critical</b> or <b>Out of Stock</b> status and require immediate attention:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr style="background-color: #F0F2F6; text-align: left;">
                            <th style="padding: 12px; border-bottom: 2px solid #29B5E8;">Location</th>
                            <th style="padding: 12px; border-bottom: 2px solid #29B5E8;">Item</th>
                            <th style="padding: 12px; border-bottom: 2px solid #29B5E8;">Status</th>
                            <th style="padding: 12px; border-bottom: 2px solid #29B5E8;">Current Stock</th>
                            <th style="padding: 12px; border-bottom: 2px solid #29B5E8;">Est. Stockout</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for _, alert in critical_items.iterrows():
            status_color = "#DC143C" if alert['STOCK_STATUS'] == 'OUT_OF_STOCK' else "#FFA500"
            html += f"""
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #EEE;">{alert['LOCATION']}</td>
                            <td style="padding: 12px; border-bottom: 1px solid #EEE;"><b>{alert['ITEM']}</b></td>
                            <td style="padding: 12px; border-bottom: 1px solid #EEE;">
                                <span style="color: {status_color}; font-weight: bold;">{alert['STOCK_STATUS']}</span>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #EEE;">{alert['CURRENT_STOCK']:.0f} units</td>
                            <td style="padding: 12px; border-bottom: 1px solid #EEE;">{alert['DAYS_UNTIL_STOCKOUT']:.1f} days</td>
                        </tr>
            """
            
        html += """
                    </tbody>
                </table>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #FFF5F5; border-left: 4px solid #DC143C; border-radius: 4px;">
                    <b>Action Required:</b> Please initiate procurement process for these items immediately via the StockPulse 360 Dashboard.
                </div>
                
                <p style="margin-top: 20px; font-size: 12px; color: #777;">
                    This is an automated message from StockPulse 360 AI-Driven Stock Monitor.<br>
                    Timestamp: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
                </p>
            </div>
        </body>
        </html>
        """
        
        self._send(subject, html)

    def _send(self, subject, html_content):
        """Execute the SMTP send process."""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ", ".join([e.strip() for e in self.to_emails])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(html_content, 'html'))
            
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
                
            print(f"✅ Alert email sent successfully to {len(self.to_emails)} recipients")
        except Exception as e:
            print(f"❌ Failed to send alert email: {e}")

if __name__ == "__main__":
    # Test script
    test_data = pd.DataFrame([{
        'LOCATION': 'Mumbai',
        'ITEM': 'Insulin',
        'STOCK_STATUS': 'OUT_OF_STOCK',
        'CURRENT_STOCK': 0,
        'DAYS_UNTIL_STOCKOUT': 0,
        'ALERT_MESSAGE': 'Critical stockout at Mumbai hospital'
    }])
    notifier = EmailNotifier()
    notifier.send_alert_email(test_data)
