"""
Critical Alerts Page
Main orchestrator for the alerts page components
"""

import streamlit as st
from utils import load_critical_alerts, section_header
from ..shared.filters import render_page_sidebar_filters
from .components import render_alert_cards, send_notifications

try:
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.metric_cards import style_metric_cards
    EXTRAS_AVAILABLE = True
except ImportError:
    EXTRAS_AVAILABLE = False


def render_alerts_page():
    """Render Critical Alerts page with its own independent filters."""
    # Load raw alerts data
    alerts_data = load_critical_alerts()
    
    # Sidebar Filters
    filtered_data = render_page_sidebar_filters(alerts_data, "Alerts")
    
    container = st.session_state.get('filter_container', st.sidebar)
    
    # Status Multi-select for Alerts
    if not filtered_data.empty:
        status_options = sorted(alerts_data['STOCK_STATUS'].unique().tolist())
        selected_status = container.multiselect("Filter by Status", status_options, default=status_options, key="alert_status_filter")
        if selected_status:
            filtered_data = filtered_data[filtered_data['STOCK_STATUS'].isin(selected_status)]
    
    # Header
    if EXTRAS_AVAILABLE:
        colored_header(
            label="Critical Alerts Dashboard",
            description="Real-time stock alerts and notifications",
            color_name="red-70"
        )
    else:
        st.markdown(section_header("Critical Alerts", "alert"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if filtered_data is not None and not filtered_data.empty:
        critical_alerts = filtered_data[filtered_data['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL'])]
        warning_alerts = filtered_data[filtered_data['STOCK_STATUS'] == 'WARNING']
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Critical Alerts", len(critical_alerts), 
                     help="Out of stock or critically low items")
        with col2:
            st.metric("Warning Alerts", len(warning_alerts),
                     help="Items approaching low stock threshold")
        with col3:
            st.metric("Total Alerts", len(filtered_data),
                     help="Active alerts matching filters")
        
        # Notification button
        send_notifications(filtered_data)
        
        if EXTRAS_AVAILABLE:
            style_metric_cards(
                background_color="#FFFFFF",
                border_left_color="#DC143C",
                border_color="#E0E0E0",
                box_shadow=True
            )
        
        st.divider()
        
        # Render alert cards
        render_alert_cards(filtered_data)
    else:
        st.success("No active critical alerts - all stock levels are healthy!")
