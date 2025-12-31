"""
Alerts Page - Notification Component
Handles sending notifications to procurement team
"""

import streamlit as st
import sys
import os

# Add python folder to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'python'))

try:
    from config import get_snowflake_session
    from alert_sender import AlertSender
    NOTIFICATION_AVAILABLE = True
except ImportError:
    NOTIFICATION_AVAILABLE = False


def send_notifications(filtered_data):
    """Send notifications for filtered alerts."""
    
    button_col1, button_col2 = st.columns([1, 4])
    with button_col1:
        if not filtered_data.empty:
            if st.button("📤 Notify Procurement", help="Send the filtered alerts to Email and Slack"):
                if not NOTIFICATION_AVAILABLE:
                    st.error("Notification system not available. Check alert_sender configuration.")
                    return
                
                with st.spinner("Sending notifications..."):
                    try:
                        session = get_snowflake_session()
                        sender = AlertSender(session)
                        sender.send_alerts(filtered_data)
                        session.close()
                        st.success(f"Notifications for {len(filtered_data)} items delivered!")
                    except Exception as e:
                        st.error(f"Failed to send notifications: {e}")
        else:
            st.button("📤 Notify Procurement", disabled=True)
