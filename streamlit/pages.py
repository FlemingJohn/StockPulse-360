"""
StockPulse 360 - Page Rendering Functions
All page-specific rendering logic for the dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils import get_svg_icon, section_header, load_stock_risk_data, load_critical_alerts
from utils import load_procurement_export, load_item_performance, get_status_color

# Streamlit extras for enhanced UI
try:
    from streamlit_extras.metric_cards import style_metric_cards
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.badges import badge
    from streamlit_extras.add_vertical_space import add_vertical_space
    EXTRAS_AVAILABLE = True
except ImportError:
    EXTRAS_AVAILABLE = False

# ============================================================================
# Filter Component
# ============================================================================

def render_filters():
    """Render filter section in main page."""
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown(section_header("Filters", "filter"), unsafe_allow_html=True)
    
    # Load data for filters
    stock_data = load_stock_risk_data()
    
    if stock_data is None or stock_data.empty:
        st.error("Unable to load data. Please check your Snowflake connection.")
        st.markdown('</div>', unsafe_allow_html=True)
        return pd.DataFrame()
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        locations = ['All'] + sorted(stock_data['LOCATION'].unique().tolist())
        selected_location = st.selectbox("Location", locations, key="filter_location")
    
    with col2:
        items = ['All'] + sorted(stock_data['ITEM'].unique().tolist())
        selected_item = st.selectbox("Item", items, key="filter_item")
    
    with col3:
        status_options = ['All', 'OUT_OF_STOCK', 'CRITICAL', 'WARNING', 'LOW', 'HEALTHY']
        selected_status = st.multiselect("Status", status_options, default=['All'], key="filter_status")
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear Filters", use_container_width=True):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_data = stock_data.copy()
    if selected_location != 'All':
        filtered_data = filtered_data[filtered_data['LOCATION'] == selected_location]
    if selected_item != 'All':
        filtered_data = filtered_data[filtered_data['ITEM'] == selected_item]
    if 'All' not in selected_status:
        filtered_data = filtered_data[filtered_data['STOCK_STATUS'].isin(selected_status)]
    
    return filtered_data

# ============================================================================
# Page: Overview & Heatmap
# ============================================================================

def render_overview_page(filtered_data):
    """Render Overview & Heatmap page."""
    # Check if data is available
    if filtered_data is None or filtered_data.empty:
        st.warning("No data available. Please check your Snowflake connection and ensure tables are populated.")
        return
    
    # KPI Metrics with enhanced styling
    if EXTRAS_AVAILABLE:
        colored_header(
            label="📊 Key Performance Metrics",
            description="Real-time stock health indicators",
            color_name="blue-70"
        )
    else:
        st.markdown(section_header("Key Metrics", "chart"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    
    st.divider()
    
    # Stock Health Heatmap
    st.markdown(section_header("Stock Health Heatmap", "map"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Heatmap View", "Table View"])
    
    with tab1:
        if not filtered_data.empty:
            # Create pivot table for heatmap
            pivot_data = filtered_data.pivot_table(
                index='LOCATION',
                columns='ITEM',
                values='HEALTH_SCORE',
                aggfunc='first'
            )
            
            if not pivot_data.empty:
                fig = px.imshow(
                    pivot_data,
                    labels=dict(x="Item", y="Location", color="Health Score"),
                    color_continuous_scale=[[0, '#DC143C'], [0.5, '#FFA500'], [1, '#29B5E8']],
                    aspect="auto",
                    title="Stock Health Score by Location and Item"
                )
                fig.update_layout(
                    height=400,
                    font=dict(family="Segoe UI, sans-serif", color="#0F4C81"),
                    title_font=dict(size=20, color="#0F4C81", family="Segoe UI"),
                    plot_bgcolor='#FFFFFF',
                    paper_bgcolor='#F0F2F6'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for heatmap.")
        else:
            st.warning("No data available for the selected filters.")
    
    with tab2:
        if not filtered_data.empty:
            # Display table
            st.dataframe(
                filtered_data[[
                    'LOCATION', 'ITEM', 'CURRENT_STOCK', 'AVG_DAILY_USAGE',
                    'DAYS_UNTIL_STOCKOUT', 'STOCK_STATUS', 'HEALTH_SCORE'
                ]],
                use_container_width=True,
                height=400
            )
        else:
            st.warning("No data available for the selected filters.")

# ============================================================================
# Page: Critical Alerts
# ============================================================================

def render_alerts_page(filtered_data):
    """Render Critical Alerts page."""
    if EXTRAS_AVAILABLE:
        colored_header(
            label="🚨 Critical Alerts Dashboard",
            description="Real-time stock alerts and notifications",
            color_name="red-70"
        )
    else:
        st.markdown(section_header("Critical Alerts", "alert"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    alerts_data = load_critical_alerts()
    
    if alerts_data is not None and not alerts_data.empty:
        critical_alerts = alerts_data[alerts_data['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL'])]
        warning_alerts = alerts_data[alerts_data['STOCK_STATUS'] == 'WARNING']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔴 Critical Alerts", len(critical_alerts), 
                     help="Out of stock or critically low items")
        with col2:
            st.metric("🟡 Warning Alerts", len(warning_alerts),
                     help="Items approaching low stock threshold")
        with col3:
            st.metric("📋 Total Alerts", len(alerts_data),
                     help="All active alerts")
        
        if EXTRAS_AVAILABLE:
            style_metric_cards(
                background_color="#FFFFFF",
                border_left_color="#DC143C",
                border_color="#E0E0E0",
                box_shadow=True
            )
        
        st.divider()
        
        # Alert cards with enhanced styling
        for idx, alert in alerts_data.iterrows():
            status = alert['STOCK_STATUS']
            css_class = "critical-alert" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "warning-alert"
            alert_svg = get_svg_icon('alert', size=20, color="#DC143C" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "#FFA500")
            
            # Add badge if extras available
            badge_html = ""
            if EXTRAS_AVAILABLE:
                badge_color = "red" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "orange"
                badge_html = f'<span style="background-color: {badge_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin-left: 10px;">{status}</span>'
            
            st.markdown(f"""
            <div class="{css_class}">
                <div style="display: flex; align-items: center; gap: 10px;">
                    {alert_svg}
                    <strong>{alert['ALERT_MESSAGE']}</strong>
                    {badge_html}
                </div>
                <div style="margin-top: 8px;">
                    📍 Location: {alert['LOCATION']} | 📦 Item: {alert['ITEM']}<br>
                    📊 Current Stock: {alert['CURRENT_STOCK']:.0f} | 📉 Avg Daily Usage: {alert['AVG_DAILY_USAGE']:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No critical alerts - all stock levels are healthy!")

# ============================================================================
# Page: Reorder Recommendations
# ============================================================================

def render_reorder_page(filtered_data):
    """Render Reorder Recommendations page."""
    if EXTRAS_AVAILABLE:
        colored_header(
            label="🛒 Reorder Recommendations",
            description="Smart procurement suggestions based on stock levels",
            color_name="green-70"
        )
    else:
        st.markdown(section_header("Reorder Recommendations", "cart"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    procurement_data = load_procurement_export()
    
    if procurement_data is not None and not procurement_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Items to Reorder", len(procurement_data),
                     help="Total items requiring reorder")
        with col2:
            total_cost = procurement_data['Estimated Cost (₹)'].sum()
            st.metric("💰 Total Estimated Cost", f"₹{total_cost:,.0f}",
                     help="Total procurement budget required")
        with col3:
            urgent_count = len(procurement_data[procurement_data['Order Within (Days)'] <= 1])
            st.metric("⚡ Urgent Orders", urgent_count,
                     help="Items needing immediate procurement")
        
        if EXTRAS_AVAILABLE:
            style_metric_cards(
                background_color="#FFFFFF",
                border_left_color="#4CAF50",
                border_color="#E0E0E0",
                box_shadow=True
            )
        
        st.divider()
        
        st.dataframe(
            procurement_data,
            use_container_width=True,
            height=500,
            column_config={
                "Order Within (Days)": st.column_config.NumberColumn(
                    "Order Within (Days)",
                    help="Days until stockout",
                    format="%d days"
                ),
                "Estimated Cost (₹)": st.column_config.NumberColumn(
                    "Estimated Cost (₹)",
                    help="Estimated procurement cost",
                    format="₹%.2f"
                )
            }
        )
        
        csv = procurement_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Procurement List (CSV)",
            data=csv,
            file_name=f"procurement_list_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    else:
        st.info("✅ No reorder recommendations at this time.")

# ============================================================================
# Page: AI/ML Insights
# ============================================================================

def render_ai_ml_page(filtered_data):
    """Render AI/ML Insights page."""
    st.markdown(section_header("AI/ML Insights", "trending"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("AI/ML features including Cortex AI forecasting, anomaly detection, and seasonal analysis.")
    
    st.markdown("### Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - **Cortex AI Demand Forecasting**  
          Predict future demand using Snowflake's native ML
        - **Anomaly Detection**  
          Identify unusual usage patterns
        """)
    with col2:
        st.markdown("""
        - **Seasonal Trend Analysis**  
          Recognize holiday spikes and patterns
        - **Predictive Analytics**  
          Forecast stockouts before they happen
        """)

# ============================================================================
# Page: Advanced Analytics
# ============================================================================

def render_analytics_page(filtered_data):
    """Render Advanced Analytics page."""
    st.markdown(section_header("Advanced Analytics", "chart"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("Advanced analytics including ABC analysis, cost optimization, and stockout impact analysis.")
    
    st.markdown("### Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - **ABC Analysis**  
          Classify inventory by value (High/Medium/Low)
        - **Cost Optimization Dashboard**  
          Track budget and ROI
        """)
    with col2:
        st.markdown("""
        - **Stockout Impact Analysis**  
          Quantify patient/beneficiary impact
        - **Budget Tracking**  
          Monitor spending and identify savings
        """)

# ============================================================================
# Page: Supplier Management
# ============================================================================

def render_supplier_page():
    """Render Supplier Management page."""
    st.markdown(section_header("Supplier Management", "box"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("Supplier integration features including purchase orders, performance tracking, and delivery schedules.")
    
    st.markdown("### Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - **Auto-Generated Purchase Orders**  
          Smart procurement based on reorder recommendations
        - **Supplier Performance Dashboard**  
          Track reliability and lead times
        """)
    with col2:
        st.markdown("""
        - **Delivery Schedule Tracking**  
          Monitor expected arrivals
        - **Cost Analysis by Supplier**  
          Optimize supplier selection
        """)
