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
from utils import load_procurement_export, load_item_performance, get_status_color, load_seasonal_forecasts, load_abc_analysis
from utils import load_stockout_impact, load_budget_tracking
from utils import load_purchase_orders, load_supplier_performance, load_supplier_comparison, load_supplier_cost_analysis, load_delivery_schedule

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
    
    # Load seasonal forecasts
    forecasts = load_seasonal_forecasts()
    
    if forecasts is not None and not forecasts.empty:
        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_forecasts = len(forecasts)
            st.metric("Total Forecasts", total_forecasts, help="Total number of AI-generated forecasts")
        with col2:
            unique_items = forecasts['item'].nunique() if 'item' in forecasts.columns else 0
            st.metric("Items Analyzed", unique_items, help="Number of unique items with forecasts")
        with col3:
            unique_locations = forecasts['location'].nunique() if 'location' in forecasts.columns else 0
            st.metric("Locations", unique_locations, help="Number of locations covered")
        with col4:
            avg_forecast = forecasts['forecasted_usage'].mean() if 'forecasted_usage' in forecasts.columns else 0
            st.metric("Avg Forecast", f"{avg_forecast:.1f}", help="Average forecasted usage")
        
        st.divider()
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["📈 Seasonal Forecasts", "📊 Forecast Data"])
        
        with tab1:
            st.markdown("### Seasonal Usage Forecasts")
            st.markdown("AI-powered forecasts based on weekly and monthly seasonal patterns")
            
            # Filter by location and item
            col1, col2 = st.columns(2)
            with col1:
                locations = ['All'] + sorted(forecasts['location'].unique().tolist()) if 'location' in forecasts.columns else ['All']
                selected_location = st.selectbox("Select Location", locations, key="ai_location")
            with col2:
                items = ['All'] + sorted(forecasts['item'].unique().tolist()) if 'item' in forecasts.columns else ['All']
                selected_item = st.selectbox("Select Item", items, key="ai_item")
            
            # Filter data
            filtered_forecasts = forecasts.copy()
            if selected_location != 'All':
                filtered_forecasts = filtered_forecasts[filtered_forecasts['location'] == selected_location]
            if selected_item != 'All':
                filtered_forecasts = filtered_forecasts[filtered_forecasts['item'] == selected_item]
            
            if not filtered_forecasts.empty:
                # Create line chart
                fig = px.line(
                    filtered_forecasts,
                    x='forecast_date',
                    y='forecasted_usage',
                    color='item' if selected_location != 'All' else 'location',
                    title=f"Seasonal Forecast - {selected_location} - {selected_item}",
                    labels={'forecasted_usage': 'Forecasted Usage', 'forecast_date': 'Date'},
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
                if 'seasonal_factor' in filtered_forecasts.columns:
                    st.markdown("#### Seasonal Adjustment Factors")
                    st.markdown("Values > 1.0 indicate higher demand, < 1.0 indicate lower demand")
                    
                    fig2 = px.bar(
                        filtered_forecasts,
                        x='forecast_date',
                        y='seasonal_factor',
                        color='seasonal_factor',
                        title="Seasonal Demand Patterns",
                        labels={'seasonal_factor': 'Seasonal Factor', 'forecast_date': 'Date'},
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
                label="📥 Download Forecast Data (CSV)",
                data=csv,
                file_name=f"seasonal_forecasts_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
    else:
        st.info("🤖 AI/ML forecasts are being generated. Please run the seasonal forecasting script to populate data.")
        st.markdown("""
        ### Available AI/ML Features
        
        **🔮 Seasonal Pattern Recognition**
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

def render_analytics_page(filtered_data):
    """Render Advanced Analytics page."""
    st.markdown(section_header("Advanced Analytics", "chart"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("📊 Advanced analytics including ABC analysis, cost optimization, and stockout impact analysis.")
    
    # Create tabs for different analytics features
    tab1, tab2, tab3 = st.tabs(["📈 ABC Analysis", "💰 Cost Optimization", "⚠️ Stockout Impact"])
    
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
                    x='item',
                    y='TOTAL_VALUE',
                    color='ABC_CATEGORY',
                    title="Item Value Distribution (ABC Classification)",
                    labels={'TOTAL_VALUE': 'Total Value (₹)', 'item': 'Item'},
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
                    names='item',
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
                abc_data[['item', 'TOTAL_VALUE', 'TOTAL_QUANTITY', 'VALUE_PERCENTAGE', 'ABC_CATEGORY', 'CATEGORY_DESCRIPTION']],
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
                status_emoji = {'HEALTHY': '✅', 'MODERATE': '🟡', 'WARNING': '🟠', 'OVER_BUDGET': '🔴'}
                st.metric("Budget Status", f"{status_emoji.get(row['BUDGET_STATUS'], '')} {row['BUDGET_STATUS']}")
            
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
                    x='item',
                    y='PATIENTS_AFFECTED_UNTIL_STOCKOUT',
                    color='IMPACT_SEVERITY',
                    facet_col='location',
                    title="Patient Impact by Item and Location",
                    labels={'PATIENTS_AFFECTED_UNTIL_STOCKOUT': 'Patients Affected', 'item': 'Item'},
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
                impact_data[['location', 'item', 'STOCK_STATUS', 'PATIENTS_AFFECTED_UNTIL_STOCKOUT', 
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
    """Render Supplier Management page."""
    st.markdown(section_header("Supplier Management", "box"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Load data
    po_data = load_purchase_orders()
    performance_data = load_supplier_performance()
    comparison_data = load_supplier_comparison()
    cost_data = load_supplier_cost_analysis()
    schedule_data = load_delivery_schedule()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Purchase Orders", 
        "🏆 Performance", 
        "⚖️ Comparison", 
        "📅 Delivery Schedule",
        "💰 Cost Analysis"
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
