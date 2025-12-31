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
from utils import load_procurement_export, load_item_performance, get_status_color, load_seasonal_forecasts, load_abc_analysis, load_reorder_recommendations
from utils import load_stockout_impact, load_budget_tracking
from utils import load_purchase_orders, load_supplier_performance, load_supplier_comparison, load_supplier_cost_analysis, load_delivery_schedule
from alert_sender import AlertSender
from config import get_snowflake_session

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

# Helper for page-specific filters
def render_page_sidebar_filters(df, page_name=""):
    """Render common sidebar filters (Location/Item) for a specific page."""
    if df is None or df.empty:
        return df
        
    # Get the container from session state or fallback to sidebar
    container = st.session_state.get('filter_container', st.sidebar)
    
    container.markdown(f'<div class="sidebar-filter-header">{page_name} Filters</div>', unsafe_allow_html=True)
    
    # Selection logic
    filtered_df = df.copy()
    
    # Location Filter
    if 'LOCATION' in df.columns:
        loc_options = ['All'] + sorted(df['LOCATION'].unique().tolist())
        selected_loc = container.selectbox("Select Location", loc_options, key=f"filter_loc_{page_name}")
        if selected_loc != 'All':
            filtered_df = filtered_df[filtered_df['LOCATION'] == selected_loc]
            
    # Item Filter
    if 'ITEM' in df.columns:
        item_options = ['All'] + sorted(filtered_df['ITEM'].unique().tolist())
        selected_item = container.selectbox("Select Item", item_options, key=f"filter_item_{page_name}")
        if selected_item != 'All':
            filtered_df = filtered_df[filtered_df['ITEM'] == selected_item]
            
    return filtered_df

def apply_sidebar_logic_to_performance(perf_df, filtered_po_df):
    """Filter performance data to match the suppliers in the filtered PO data."""
    if perf_df is None or perf_df.empty or filtered_po_df is None or filtered_po_df.empty:
        return perf_df
    
    # Get unique suppliers from filtered POs
    valid_suppliers = filtered_po_df['SUPPLIER_NAME'].unique()
    return perf_df[perf_df['SUPPLIER_NAME'].isin(valid_suppliers)]

# ============================================================================
# Page: Overview & Heatmap
# ============================================================================

def render_overview_page():
    """Render Overview & Heatmap page with its own filters."""
    # Load raw data
    stock_data = load_stock_risk_data()
    
    # Sidebar Filters
    filtered_data = render_page_sidebar_filters(stock_data, "Overview")
    
    container = st.session_state.get('filter_container', st.sidebar)
    
    # Additional Status Filter for Overview
    if not filtered_data.empty and 'STOCK_STATUS' in filtered_data.columns:
        status_options = ['All'] + sorted(filtered_data['STOCK_STATUS'].unique().tolist())
        selected_status = container.multiselect("Stock Status", status_options, default=['All'], key="ov_status")
        if 'All' not in selected_status and selected_status:
            filtered_data = filtered_data[filtered_data['STOCK_STATUS'].isin(selected_status)]

    # Check if data is available after filtering
    if filtered_data is None or filtered_data.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # KPI Metrics with enhanced styling
    if EXTRAS_AVAILABLE:
        colored_header(
            label="Key Performance Metrics",
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
        
        # Action Buttons
        button_col1, button_col2 = st.columns([1, 4])
        with button_col1:
            if not filtered_data.empty:
                if st.button("📤 Notify Procurement", help="Send the filtered alerts to Email and Slack"):
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
        
        if EXTRAS_AVAILABLE:
            style_metric_cards(
                background_color="#FFFFFF",
                border_left_color="#DC143C",
                border_color="#E0E0E0",
                box_shadow=True
            )
        
        st.divider()
        
        if filtered_data.empty:
            st.info("No alerts match the selected filters.")
        else:
            # Alert cards with enhanced styling
            for idx, alert in filtered_data.iterrows():
                status = alert['STOCK_STATUS']
                css_class = "critical-alert" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "warning-alert"
                alert_color = "#DC143C" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "#FFA500"
                alert_svg = get_svg_icon('alert', size=24, color=alert_color)
                
                # Risk Level Badge
                risk_badge = f'<span style="background-color: {alert_color}; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; margin-left: auto;">{status.replace("_", " ")}</span>'
                
                st.markdown(f"""
                <div class="{css_class}">
                    <div style="display: flex; align-items: flex-start; gap: 15px;">
                        <div style="background: rgba(255,255,255,0.5); padding: 10px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                            {alert_svg}
                        </div>
                        <div style="flex-grow: 1;">
                            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                <span style="font-size: 1.1rem; font-weight: 700; color: #0F4C81;">{alert['ITEM']}</span>
                                {risk_badge}
                            </div>
                            <div style="font-size: 0.95rem; color: #333; margin-bottom: 12px; line-height: 1.4;">
                                {alert['ALERT_MESSAGE']}
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 15px; background: rgba(255,255,255,0.3); padding: 8px 12px; border-radius: 8px; font-size: 0.85rem;">
                                <div style="display: flex; align-items: center; gap: 5px;">
                                    {get_svg_icon('location', size=14, color="#333")} <span style="font-weight: 600;">{alert['LOCATION']}</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 5px;">
                                    {get_svg_icon('box', size=14, color="#333")} Stock: <span style="font-weight: 600; color: {alert_color};">{alert['CURRENT_STOCK']:.0f} units</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 5px;">
                                    {get_svg_icon('trending', size=14, color="#333")} Usage: <span style="font-weight: 600;">{alert['AVG_DAILY_USAGE']:.1f}/day</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 5px;">
                                    {get_svg_icon('hourglass', size=14, color="#333")} Remaining: <span style="font-weight: 600;">{alert['DAYS_UNTIL_STOCKOUT']:.1f} days</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("No active critical alerts - all stock levels are healthy!")

# ============================================================================
# Page: Reorder Recommendations
# ============================================================================

def render_reorder_page():
    """Render Reorder Recommendations page with its own filters."""
    container = st.session_state.get('filter_container', st.sidebar)
    
    # Sidebar Controls for Simulation (at the top)
    container.markdown(f'<div class="sidebar-filter-header">Simulation Settings</div>', unsafe_allow_html=True)
    
    # Dynamic Safety Days Slider with Session State
    if 'safety_days_sim' not in st.session_state:
        st.session_state['safety_days_sim'] = 30
        
    def reset_simulation():
        st.session_state['safety_days_sim'] = 30
        
    container.button("Reset Simulation", use_container_width=True, on_click=reset_simulation)
    
    safety_days = container.slider(
        "Secure Stock For (Days)", 
        min_value=14, 
        max_value=120, 
        key='safety_days_sim',
        step=7,
        help="Simulate the budget needed to secure stock for a specific duration."
    )
    
    # Load raw data
    raw_procurement = load_reorder_recommendations()
    po_data = load_purchase_orders()
    
    # Sidebar Filters - apply to raw data first
    filtered_data = render_page_sidebar_filters(raw_procurement, "Reorder")
    
    # Join with PO Data to get Best Supplier and Reliability Score
    if not filtered_data.empty and not po_data.empty:
        # Merge to get supplier info
        # Note: po_data has LOCATION, ITEM, SUPPLIER_NAME, RELIABILITY_SCORE
        filtered_data = filtered_data.merge(
            po_data[['LOCATION', 'ITEM', 'SUPPLIER_NAME', 'RELIABILITY_SCORE']], 
            on=['LOCATION', 'ITEM'], 
            how='left'
        )
        # Fill missing scores/names
        filtered_data['SUPPLIER_NAME'] = filtered_data['SUPPLIER_NAME'].fillna('N/A')
        filtered_data['RELIABILITY_SCORE'] = filtered_data['RELIABILITY_SCORE'].fillna(75.0)

    # Dynamic Recalculation based on Safety Days (Standardized to UPPERCASE)
    if not filtered_data.empty:
        # Reset index to avoid alignment issues during calculation
        filtered_data = filtered_data.reset_index(drop=True)
        
        # Recalculate based on Slider
        # Simulation Quantity = (safety_days - days_until_stockout) * avg_usage
        filtered_data['SIMULATION_QUANTITY'] = (safety_days - filtered_data['DAYS_UNTIL_STOCKOUT']).clip(lower=0) * filtered_data['AVG_DAILY_USAGE']
        filtered_data['SIMULATION_QUANTITY'] = filtered_data['SIMULATION_QUANTITY'].fillna(0)
        
        # Calculate Unit Cost (Estimated Cost / Reorder Quantity)
        # If Reorder Quantity is 0, we can't get unit cost easily, fallback to 10
        filtered_data['UNIT_COST'] = filtered_data['ESTIMATED_COST'] / filtered_data['REORDER_QUANTITY'].replace(0, 1)
        filtered_data['UNIT_COST'] = filtered_data['UNIT_COST'].fillna(10.0)
        filtered_data['SIMULATION_COST'] = filtered_data['SIMULATION_QUANTITY'] * filtered_data['UNIT_COST']
        filtered_data['SIMULATION_COST'] = filtered_data['SIMULATION_COST'].fillna(0)
        
        # Calculate Delta from 30-day baseline
        filtered_data['COST_DELTA'] = filtered_data['SIMULATION_COST'] - filtered_data['ESTIMATED_COST']
        filtered_data['QTY_DELTA'] = filtered_data['SIMULATION_QUANTITY'] - filtered_data['REORDER_QUANTITY']

    if EXTRAS_AVAILABLE:
        colored_header(
            label="Reorder Recommendations",
            description=f"Smart suggestions simulating {safety_days} days of coverage",
            color_name="green-70"
        )
    else:
        st.markdown(section_header("Reorder Recommendations", "cart"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if filtered_data is not None and not filtered_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Items to Reorder", len(filtered_data),
                     help="Total items requiring reorder")
        with col2:
            total_cost = filtered_data['SIMULATION_COST'].sum()
            delta_cost = filtered_data['COST_DELTA'].sum()
            st.metric("Total Estimated Cost", f"₹{total_cost:,.0f}",
                     delta=f"₹{delta_cost:,.0f} vs Baseline", delta_color="inverse",
                     help=f"Projected budget for {safety_days} days of stock")
        with col3:
            urgent_count = len(filtered_data[filtered_data['DAYS_UNTIL_STOCKOUT'] <= 1])
            st.metric("Urgent Orders", urgent_count,
                     help="Items needing immediate procurement")
        
        if EXTRAS_AVAILABLE:
            style_metric_cards(
                background_color="#FFFFFF",
                border_left_color="#4CAF50",
                border_color="#E0E0E0",
                box_shadow=True
            )
        
        st.divider()

        # Procurement Strategy Matrix (Bubble Chart)
        st.subheader("Procurement Strategy Matrix")
        st.markdown(f"*Strategic view of Urgency vs. Investment (Simulated: **{safety_days} Days**)*")
        
        # Create bubble chart
        fig = px.scatter(
            filtered_data,
            x="DAYS_UNTIL_STOCKOUT",
            y="SIMULATION_COST",
            size="SIMULATION_QUANTITY",
            color="RELIABILITY_SCORE",
            hover_name="ITEM",
            custom_data=['ESTIMATED_COST', 'REORDER_QUANTITY', 'COST_DELTA', 'SIMULATION_QUANTITY'],
            labels={
                "DAYS_UNTIL_STOCKOUT": "Order Within (Days)",
                "SIMULATION_COST": "Simulated Cost (₹)",
                "RELIABILITY_SCORE": "Reliability (%)",
                "SIMULATION_QUANTITY": "Simulated Qty"
            },
            color_continuous_scale="RdYlGn",
            template="plotly_white",
            height=500,
            size_max=40,
            range_x=[-1, max(30, filtered_data['DAYS_UNTIL_STOCKOUT'].max() * 1.1)],
            range_y=[0, max(1000, filtered_data['SIMULATION_COST'].max() * 1.2)]
        )
        
        fig.update_traces(
            hovertemplate="<br>".join([
                "<b>%{hovertext}</b>",
                "Ugency: Within %{x} days",
                "Simulated Cost: ₹%{y:,.0f}",
                "Simulated Qty: %{customdata[3]:,.0f}",
                "-----------------------",
                "Baseline Cost: ₹%{customdata[0]:,.0f}",
                "Baseline Qty: %{customdata[1]:,.0f}",
                "Delta: ₹%{customdata[2]:,.0f}",
                "<extra></extra>"
            ])
        )
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            hovermode="closest",
            coloraxis_colorbar=dict(title="Reliability %")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()

        # Custom Dataframe with High Risk highlighting
        def highlight_risk(row):
            if row['Supplier Reliability (%)'] < 75:
                return ['background-color: #ffebee; border-left: 5px solid #ef5350'] * len(row)
            return [''] * len(row)

        display_df = filtered_data.copy()
        
        # Select and Rename for clarity in display
        display_df = display_df[[
            'LOCATION', 'ITEM', 'CURRENT_STOCK', 'DAYS_UNTIL_STOCKOUT', 
            'SIMULATION_QUANTITY', 'SIMULATION_COST', 'SUPPLIER_NAME', 'RELIABILITY_SCORE'
        ]]
        
        display_df = display_df.rename(columns={
            'LOCATION': 'Location',
            'ITEM': 'Item Name',
            'CURRENT_STOCK': 'Current Stock',
            'DAYS_UNTIL_STOCKOUT': 'Order Within (Days)',
            'SIMULATION_COST': 'Total Cost (₹)',
            'SIMULATION_QUANTITY': 'Order Quantity',
            'SUPPLIER_NAME': 'Supplier',
            'RELIABILITY_SCORE': 'Supplier Reliability (%)'
        })

        st.dataframe(
            display_df.style.apply(highlight_risk, axis=1),
            use_container_width=True,
            height=500,
            column_config={
                "Order Within (Days)": st.column_config.NumberColumn(
                    "Order Within (Days)",
                    help="Days until stockout",
                    format="%d days"
                ),
                "Total Cost (₹)": st.column_config.NumberColumn(
                    "Total Cost (₹)",
                    help="Estimated procurement cost for selected safety days",
                    format="₹%.2f"
                ),
                "Supplier Reliability (%)": st.column_config.ProgressColumn(
                    "Supplier Reliability (%)",
                    help="Supplier performance score",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100
                )
            }
        )
        
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download Procurement List (CSV)",
            data=csv,
            file_name=f"procurement_list_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    else:
        st.info("No reorder recommendations at this time.")

# ============================================================================
# Page: AI/ML Insights
# ============================================================================

def render_ai_ml_page():
    """Render AI/ML Insights page with independent filters."""
    # Load raw forecasts
    forecasts = load_seasonal_forecasts()
    
    # Sidebar Filters
    filtered_data = render_page_sidebar_filters(forecasts, "AI/ML")
    
    st.markdown(section_header("AI/ML Insights", "trending"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if filtered_data is not None and not filtered_data.empty:
        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_forecasts = len(forecasts)
            st.metric("Total Forecasts", total_forecasts, help="Total number of AI-generated forecasts")
        with col2:
            unique_items = forecasts['ITEM'].nunique() if 'ITEM' in forecasts.columns else 0
            st.metric("Items Analyzed", unique_items, help="Number of unique items with forecasts")
        with col3:
            unique_locations = forecasts['LOCATION'].nunique() if 'LOCATION' in forecasts.columns else 0
            st.metric("Locations", unique_locations, help="Number of locations covered")
        with col4:
            avg_forecast = forecasts['FORECASTED_USAGE'].mean() if 'FORECASTED_USAGE' in forecasts.columns else 0
            st.metric("Avg Forecast", f"{avg_forecast:.1f}", help="Average forecasted usage")
        
        st.divider()
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["Seasonal Forecasts", "Forecast Data"])
        
        with tab1:
            st.markdown("### Seasonal Usage Forecasts")
            st.markdown("AI-powered forecasts based on weekly and monthly seasonal patterns")
            
            # Filter by location and item
            col1, col2 = st.columns(2)
            with col1:
                locations = ['All'] + sorted(forecasts['LOCATION'].unique().tolist()) if 'LOCATION' in forecasts.columns else ['All']
                selected_location = st.selectbox("Select Location", locations, key="ai_location")
            with col2:
                items = ['All'] + sorted(forecasts['ITEM'].unique().tolist()) if 'ITEM' in forecasts.columns else ['All']
                selected_item = st.selectbox("Select Item", items, key="ai_item")
            
            # Filter data
            filtered_forecasts = forecasts.copy()
            if selected_location != 'All':
                filtered_forecasts = filtered_forecasts[filtered_forecasts['LOCATION'] == selected_location]
            if selected_item != 'All':
                filtered_forecasts = filtered_forecasts[filtered_forecasts['ITEM'] == selected_item]
            
            if not filtered_forecasts.empty:
                # Create line chart
                fig = px.line(
                    filtered_forecasts,
                    x='FORECAST_DATE',
                    y='FORECASTED_USAGE',
                    color='ITEM' if selected_location != 'All' else 'LOCATION',
                    title=f"Seasonal Forecast - {selected_location} - {selected_item}",
                    labels={'FORECASTED_USAGE': 'Forecasted Usage', 'FORECAST_DATE': 'Date'},
                    markers=True
                )
                fig.update_layout(
                    height=400,
                    font=dict(family="Segoe UI, sans-serif", color="#0F4C81"),
                    title_font=dict(size=18, color="#0F4C81"),
                    plot_bgcolor='#FFFFFF',
                    paper_bgcolor='#F0F2F6',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show seasonal factors
                if 'SEASONAL_FACTOR' in filtered_forecasts.columns:
                    st.markdown("#### Seasonal Adjustment Factors")
                    st.markdown("Values > 1.0 indicate higher demand, < 1.0 indicate lower demand")
                    
                    fig2 = px.bar(
                        filtered_forecasts,
                        x='FORECAST_DATE',
                        y='SEASONAL_FACTOR',
                        color='SEASONAL_FACTOR',
                        title="Seasonal Demand Patterns",
                        labels={'SEASONAL_FACTOR': 'Seasonal Factor', 'FORECAST_DATE': 'Date'},
                        color_continuous_scale=[[0, '#DC143C'], [0.5, '#FFA500'], [1, '#29B5E8']]
                    )
                    fig2.update_layout(
                        height=300,
                        font=dict(family="Segoe UI, sans-serif", color="#0F4C81"),
                        plot_bgcolor='#FFFFFF',
                        paper_bgcolor='#F0F2F6'
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No forecast data available for the selected filters.")
        
        with tab2:
            st.markdown("### Forecast Data Table")
            st.dataframe(
                forecasts,
                use_container_width=True,
                height=400
            )
            
            # Download button
            csv = forecasts.to_csv(index=False)
            from datetime import datetime
            st.download_button(
                label="Download Forecast Data (CSV)",
                data=csv,
                file_name=f"seasonal_forecasts_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
    else:
        st.info("AI/ML forecasts are being generated. Please run the seasonal forecasting script to populate data.")
        st.markdown("""
        ### Available AI/ML Features
        
        **Seasonal Pattern Recognition**
        - Analyzes weekly and monthly usage patterns
        - Identifies high/low demand days
        - Generates seasonally-adjusted forecasts
        
        **📊 To Generate Forecasts:**
        ```bash
        python python/seasonal_forecaster.py
        ```
        
        **📈 Coming Soon:**
        - Cortex AI demand forecasting
        - Anomaly detection alerts
        - Predictive stock-out warnings
        """)

# ============================================================================
# Page: Advanced Analytics
# ============================================================================

def render_analytics_page():
    """Render Advanced Analytics page."""
    st.markdown(section_header("Advanced Analytics", "chart"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("Advanced analytics including ABC analysis, cost optimization, and stockout impact analysis.")
    
    # Create tabs for different analytics features
    tab1, tab2, tab3 = st.tabs(["ABC Analysis", "Cost Optimization", "Stockout Impact"])
    
    with tab1:
        st.markdown("### ABC Analysis")
        st.markdown("Classify inventory by value contribution (Pareto Principle)")
        
        # Load ABC data
        abc_data = load_abc_analysis()
        
        if not abc_data.empty:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                a_items = len(abc_data[abc_data['ABC_CATEGORY'] == 'A'])
                st.metric("Category A Items", a_items, help="High-value critical items")
            with col2:
                b_items = len(abc_data[abc_data['ABC_CATEGORY'] == 'B'])
                st.metric("Category B Items", b_items, help="Medium-value items")
            with col3:
                c_items = len(abc_data[abc_data['ABC_CATEGORY'] == 'C'])
                st.metric("Category C Items", c_items, help="Low-value items")
            
            st.markdown("")
            
            # ABC Distribution Chart
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart showing value by item
                fig = px.bar(
                    abc_data,
                    x='ITEM',
                    y='TOTAL_VALUE',
                    color='ABC_CATEGORY',
                    title="Item Value Distribution (ABC Classification)",
                    labels={'TOTAL_VALUE': 'Total Value (₹)', 'ITEM': 'Item'},
                    color_discrete_map={'A': '#DC143C', 'B': '#FFA500', 'C': '#32CD32'}
                )
                fig.update_layout(
                    height=400,
                    font=dict(family="Segoe UI, sans-serif", color="#0F4C81"),
                    plot_bgcolor='#FFFFFF',
                    paper_bgcolor='#F0F2F6'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Pie chart showing value percentage
                fig2 = px.pie(
                    abc_data,
                    values='TOTAL_VALUE',
                    names='ITEM',
                    title="Value Contribution",
                    color='ABC_CATEGORY',
                    color_discrete_map={'A': '#DC143C', 'B': '#FFA500', 'C': '#32CD32'}
                )
                fig2.update_layout(
                    height=400,
                    font=dict(family="Segoe UI, sans-serif", color="#0F4C81")
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Data table
            st.markdown("#### ABC Classification Details")
            st.dataframe(
                abc_data[['ITEM', 'TOTAL_VALUE', 'TOTAL_QUANTITY', 'VALUE_PERCENTAGE', 'ABC_CATEGORY', 'CATEGORY_DESCRIPTION']],
                use_container_width=True,
                height=200
            )
        else:
            st.info("🔧 ABC Analysis view not found. Run `python/create_abc_view.py` to create it.")
    
    with tab2:
        st.markdown("### Cost Optimization Dashboard")
        st.markdown("Track budget, identify savings, and optimize procurement costs")
        
        # Load budget data
        budget_data = load_budget_tracking()
        
        if not budget_data.empty:
            row = budget_data.iloc[0]
            
            # Budget metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Monthly Budget", f"₹{row['MONTHLY_BUDGET']:,.0f}")
            with col2:
                st.metric("Estimated Spend", f"₹{row['ESTIMATED_SPEND']:,.0f}")
            with col3:
                delta_color = "inverse" if row['REMAINING_BUDGET'] < 0 else "normal"
                st.metric("Remaining Budget", f"₹{row['REMAINING_BUDGET']:,.0f}", 
                         delta=f"{row['BUDGET_UTILIZATION_PCT']:.1f}%")
            with col4:
                status_icon = {'HEALTHY': 'check', 'MODERATE': 'info', 'WARNING': 'alert', 'OVER_BUDGET': 'alert'}
                icon_svg = get_svg_icon(status_icon.get(row['BUDGET_STATUS'], 'info'), size=18)
                st.markdown(f"**Budget Status:** {icon_svg} {row['BUDGET_STATUS']}", unsafe_allow_html=True)
            
            # Budget visualization
            import plotly.graph_objects as go
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = row['BUDGET_UTILIZATION_PCT'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Budget Utilization %"},
                delta = {'reference': 100},
                gauge = {
                    'axis': {'range': [None, 200]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 75], 'color': "#32CD32"},
                        {'range': [75, 90], 'color': "#FFD700"},
                        {'range': [90, 100], 'color': "#FFA500"},
                        {'range': [100, 200], 'color': "#DC143C"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 100}}
            ))
            fig.update_layout(height=300, font=dict(family="Segoe UI, sans-serif"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🔧 Budget tracking view not found. Run `python/create_advanced_views.py` to create it.")
    
    with tab3:
        st.markdown("### Stockout Impact Analysis")
        st.markdown("Quantify the patient/beneficiary impact of stock-outs")
        
        # Load stockout impact data
        impact_data = load_stockout_impact()
        
        if not impact_data.empty:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_affected = impact_data['PATIENTS_AFFECTED_UNTIL_STOCKOUT'].sum()
                st.metric("Total Patients Affected", f"{total_affected:,.0f}")
            with col2:
                critical_items = len(impact_data[impact_data['IMPACT_SEVERITY'].isin(['LIFE_THREATENING', 'HIGH_SEVERITY'])])
                st.metric("Critical Items", critical_items)
            with col3:
                avg_priority = impact_data['ACTION_PRIORITY'].mean()
                st.metric("Avg Action Priority", f"{avg_priority:.1f}")
            
            # Impact severity distribution
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart by item and severity
                fig = px.bar(
                    impact_data.sort_values('ACTION_PRIORITY'),
                    x='ITEM',
                    y='PATIENTS_AFFECTED_UNTIL_STOCKOUT',
                    color='IMPACT_SEVERITY',
                    facet_col='LOCATION',
                    title="Patient Impact by Item and Location",
                    labels={'PATIENTS_AFFECTED_UNTIL_STOCKOUT': 'Patients Affected', 'ITEM': 'Item'},
                    color_discrete_map={
                        'LIFE_THREATENING': '#8B0000',
                        'HIGH_SEVERITY': '#DC143C',
                        'MODERATE_SEVERITY': '#FFA500',
                        'LOW_SEVERITY': '#FFD700'
                    }
                )
                fig.update_layout(
                    height=400,
                    font=dict(family="Segoe UI, sans-serif", color="#0F4C81"),
                    plot_bgcolor='#FFFFFF'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Severity pie chart
                severity_counts = impact_data['IMPACT_SEVERITY'].value_counts()
                fig2 = px.pie(
                    values=severity_counts.values,
                    names=severity_counts.index,
                    title="Impact Severity Distribution",
                    color=severity_counts.index,
                    color_discrete_map={
                        'LIFE_THREATENING': '#8B0000',
                        'HIGH_SEVERITY': '#DC143C',
                        'MODERATE_SEVERITY': '#FFA500',
                        'LOW_SEVERITY': '#FFD700'
                    }
                )
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Data table
            st.markdown("#### Priority Action Items")
            st.dataframe(
                impact_data[['LOCATION', 'ITEM', 'STOCK_STATUS', 'PATIENTS_AFFECTED_UNTIL_STOCKOUT', 
                            'IMPACT_SEVERITY', 'ACTION_PRIORITY', 'ABC_CATEGORY']].sort_values('ACTION_PRIORITY'),
                use_container_width=True,
                height=300
            )
        else:
            st.info("🔧 Stockout impact view not found. Run `python/create_advanced_views.py` to create it.")


# ============================================================================
# Page: Supplier Management
# ============================================================================

def render_supplier_page():
    """Render Supplier Management page with independent filters."""
    # Load raw data
    po_data = load_purchase_orders()
    performance_data = load_supplier_performance()
    
    # Sidebar Filters
    filtered_po = render_page_sidebar_filters(po_data, "Supplier PO")
    filtered_performance = apply_sidebar_logic_to_performance(performance_data, filtered_po)
    
    st.markdown(section_header("Supplier Management", "box"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Use filtered data for variables below
    po_data = filtered_po
    performance_data = filtered_performance
    comparison_data = load_supplier_comparison() # Not easily filterable by location/item in current schema
    cost_data = load_supplier_cost_analysis()
    schedule_data = load_delivery_schedule()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Purchase Orders", 
        "Performance", 
        "Comparison", 
        "Delivery Schedule",
        "Cost Analysis"
    ])
    
    with tab1:
        st.markdown("### Active Purchase Orders")
        if not po_data.empty:
            st.dataframe(
                po_data[['PURCHASE_ORDER_ID', 'LOCATION', 'ITEM', 'SUPPLIER_NAME', 'ORDER_QUANTITY', 'TOTAL_COST', 'ORDER_PRIORITY', 'EXPECTED_DELIVERY_DATE']],
                use_container_width=True,
                height=400
            )
        else:
            st.info("No active purchase orders found.")
            
    with tab2:
        st.markdown("### Supplier Performance Metrics")
        if not performance_data.empty:
            # KPI Cards
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_reliability = performance_data['RELIABILITY_SCORE'].mean()
                st.metric("Avg Reliability", f"{avg_reliability:.1f}%")
            with col2:
                total_pos = performance_data['TOTAL_ORDERS'].sum()
                st.metric("Total Orders", f"{total_pos:,.0f}")
            with col3:
                on_time_pct = performance_data['ACTUAL_ON_TIME_PCT'].mean()
                st.metric("On-Time Rate", f"{on_time_pct:.1f}%")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Reliability Bar Chart
            fig = px.bar(
                performance_data,
                x='SUPPLIER_NAME',
                y='RELIABILITY_SCORE',
                color='PERFORMANCE_RATING',
                title="Supplier Reliability Scores",
                labels={'RELIABILITY_SCORE': 'Reliability (%)', 'SUPPLIER_NAME': 'Supplier'},
                color_discrete_map={'EXCELLENT': '#32CD32', 'GOOD': '#29B5E8', 'AVERAGE': '#FFA500', 'POOR': '#DC143C'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(performance_data, use_container_width=True)
        else:
            st.info("Performance data not available.")
            
    with tab3:
        st.markdown("### Supplier Comparison by Item")
        if not comparison_data.empty:
            selected_item = st.selectbox("Select Item to Compare Suppliers", comparison_data['ITEM'].unique())
            item_comp = comparison_data[comparison_data['ITEM'] == selected_item]
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.scatter(
                    item_comp,
                    x='UNIT_PRICE',
                    y='RELIABILITY_SCORE',
                    size='OVERALL_SCORE',
                    color='SUPPLIER_NAME',
                    text='SUPPLIER_NAME',
                    title=f"Price vs. Reliability - {selected_item}",
                    labels={'UNIT_PRICE': 'Unit Price (₹)', 'RELIABILITY_SCORE': 'Reliability (%)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f"#### Recommended Ranking for {selected_item}")
                for idx, row in item_comp.sort_values('SUPPLIER_RANK').iterrows():
                    st.markdown(f"**#{row['SUPPLIER_RANK']} {row['SUPPLIER_NAME']}** (Score: {row['OVERALL_SCORE']})")
                    st.progress(row['OVERALL_SCORE']/100)
        else:
            st.info("Comparison data not available.")
            
    with tab4:
        st.markdown("### Upcoming Delivery Schedule")
        if not schedule_data.empty:
            # Timeline view
            fig = px.timeline(
                schedule_data, 
                x_start="EXPECTED_DELIVERY_DATE", 
                x_end="EXPECTED_DELIVERY_DATE", 
                y="ITEM", 
                color="ORDER_PRIORITY",
                hover_data=['SUPPLIER_NAME', 'ORDER_QUANTITY', 'LOCATION'],
                title="Delivery Timeline"
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(schedule_data, use_container_width=True)
        else:
            st.info("No upcoming deliveries scheduled.")
            
    with tab5:
        st.markdown("### Procurement Cost Analysis")
        if not cost_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(
                    cost_data, 
                    values='TOTAL_SPEND', 
                    names='SUPPLIER_NAME', 
                    title="Spending Distribution by Supplier",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    cost_data,
                    x='SUPPLIER_NAME',
                    y='TOTAL_SPEND',
                    title="Total Spending by Supplier (₹)",
                    labels={'TOTAL_SPEND': 'Total Spend (₹)', 'SUPPLIER_NAME': 'Supplier'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(cost_data, use_container_width=True)
        else:
            st.info("Cost analysis data not available.")
