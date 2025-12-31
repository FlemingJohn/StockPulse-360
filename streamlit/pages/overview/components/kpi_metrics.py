"""
Overview Page - KPI Metrics Component
Displays 5 key performance indicator metrics
"""

import streamlit as st

try:
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.metric_cards import style_metric_cards
    EXTRAS_AVAILABLE = True
except ImportError:
    EXTRAS_AVAILABLE = False


def render_kpi_metrics(filtered_data):
    """Render 5 KPI metric cards for the overview page."""
    
    # Header
    if EXTRAS_AVAILABLE:
        colored_header(
            label="Key Performance Metrics",
            description="Real-time stock health indicators",
            color_name="blue-70"
        )
    else:
        from utils import section_header
        st.markdown(section_header("Key Metrics", "chart"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 5 metric columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_items = len(filtered_data)
        st.metric("Total Items", total_items, help="Total number of items tracked")
    
    with col2:
        critical_count = len(filtered_data[filtered_data['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL'])])
        st.metric("Critical Items", critical_count, delta=f"-{critical_count}", delta_color="inverse", 
                 help="Items requiring immediate attention")
    
    with col3:
        warning_count = len(filtered_data[filtered_data['STOCK_STATUS'] == 'WARNING'])
        st.metric("Warning Items", warning_count, help="Items approaching low stock")
    
    with col4:
        healthy_count = len(filtered_data[filtered_data['STOCK_STATUS'] == 'HEALTHY'])
        st.metric("Healthy Items", healthy_count, delta=f"+{healthy_count}", delta_color="normal",
                 help="Items with adequate stock levels")
    
    with col5:
        avg_health = filtered_data['HEALTH_SCORE'].mean() if not filtered_data.empty else 0
        st.metric("Avg Health Score", f"{avg_health:.1f}", help="Average health score (0-100)")
    
    # Apply metric card styling if available
    if EXTRAS_AVAILABLE:
        style_metric_cards(
            background_color="#FFFFFF",
            border_left_color="#29B5E8",
            border_color="#E0E0E0",
            box_shadow=True
        )
