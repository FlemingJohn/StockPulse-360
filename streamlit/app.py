"""
StockPulse 360 - Streamlit Dashboard
Main dashboard application for stock health monitoring
Reference: https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# For Snowflake Streamlit (runs inside Snowflake)
try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    IN_SNOWFLAKE = True
except:
    # For local development
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))
    from config import get_snowflake_session
    session = get_snowflake_session()
    IN_SNOWFLAKE = False

# ============================================================================
# Page Configuration
# ============================================================================
st.set_page_config(
    page_title="StockPulse 360",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Custom CSS
# ============================================================================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .critical-alert {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc143c;
        margin-bottom: 0.5rem;
    }
    .warning-alert {
        background-color: #fff4e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffa500;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Helper Functions
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_stock_risk_data():
    """Load stock risk data from Snowflake."""
    df = session.table("stock_risk").to_pandas()
    return df

@st.cache_data(ttl=300)
def load_critical_alerts():
    """Load critical alerts."""
    df = session.table("critical_alerts").to_pandas()
    return df

@st.cache_data(ttl=300)
def load_location_summary():
    """Load location summary."""
    df = session.table("location_summary").to_pandas()
    return df

@st.cache_data(ttl=300)
def load_procurement_export():
    """Load procurement recommendations."""
    df = session.table("procurement_export").to_pandas()
    return df

@st.cache_data(ttl=300)
def load_item_performance():
    """Load item performance data."""
    df = session.table("item_performance").to_pandas()
    return df

def get_status_color(status):
    """Get color for stock status."""
    colors = {
        'OUT_OF_STOCK': '#8B0000',
        'CRITICAL': '#DC143C',
        'WARNING': '#FFA500',
        'LOW': '#FFD700',
        'HEALTHY': '#32CD32'
    }
    return colors.get(status, '#808080')

# ============================================================================
# Main Dashboard
# ============================================================================

def main():
    # Header
    st.markdown('<div class="main-header">📊 StockPulse 360</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">AI-Driven Stock Health Monitor for Hospitals & Public Distribution Systems</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        
        # Filters
        st.subheader("🔍 Filters")
        
        # Load data for filters
        stock_data = load_stock_risk_data()
        
        locations = ['All'] + sorted(stock_data['LOCATION'].unique().tolist())
        selected_location = st.selectbox("Location", locations)
        
        items = ['All'] + sorted(stock_data['ITEM'].unique().tolist())
        selected_item = st.selectbox("Item", items)
        
        status_options = ['All', 'OUT_OF_STOCK', 'CRITICAL', 'WARNING', 'LOW', 'HEALTHY']
        selected_status = st.multiselect("Status", status_options, default=['All'])
        
        st.divider()
        
        # Info
        st.subheader("ℹ️ About")
        st.info("""
        **StockPulse 360** helps hospitals, ration shops, and NGOs:
        - Monitor stock health in real-time
        - Predict stock-outs early
        - Get reorder recommendations
        - Prevent waste and shortages
        """)
    
    # Apply filters
    filtered_data = stock_data.copy()
    if selected_location != 'All':
        filtered_data = filtered_data[filtered_data['LOCATION'] == selected_location]
    if selected_item != 'All':
        filtered_data = filtered_data[filtered_data['ITEM'] == selected_item]
    if 'All' not in selected_status:
        filtered_data = filtered_data[filtered_data['STOCK_STATUS'].isin(selected_status)]
    
    # ========================================================================
    # KPI Metrics
    # ========================================================================
    st.header("📈 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_items = len(filtered_data)
        st.metric("Total Items", total_items)
    
    with col2:
        critical_count = len(filtered_data[filtered_data['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL'])])
        st.metric("Critical Items", critical_count, delta=None, delta_color="inverse")
    
    with col3:
        warning_count = len(filtered_data[filtered_data['STOCK_STATUS'] == 'WARNING'])
        st.metric("Warning Items", warning_count)
    
    with col4:
        healthy_count = len(filtered_data[filtered_data['STOCK_STATUS'] == 'HEALTHY'])
        st.metric("Healthy Items", healthy_count, delta=None, delta_color="normal")
    
    with col5:
        avg_health = filtered_data['HEALTH_SCORE'].mean()
        st.metric("Avg Health Score", f"{avg_health:.1f}")
    
    st.divider()
    
    # ========================================================================
    # Stock Health Heatmap
    # ========================================================================
    st.header("🗺️ Stock Health Heatmap")
    
    tab1, tab2 = st.tabs(["📊 Heatmap View", "📋 Table View"])
    
    with tab1:
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
                color_continuous_scale='RdYlGn',
                aspect="auto",
                title="Stock Health Score by Location and Item"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected filters.")
    
    with tab2:
        # Display as styled dataframe
        if not filtered_data.empty:
            display_df = filtered_data[['LOCATION', 'ITEM', 'CURRENT_STOCK', 'AVG_DAILY_USAGE', 
                                       'DAYS_UNTIL_STOCKOUT', 'STOCK_STATUS', 'HEALTH_SCORE']]
            
            st.dataframe(
                display_df.style.background_gradient(subset=['HEALTH_SCORE'], cmap='RdYlGn'),
                use_container_width=True,
                height=400
            )
        else:
            st.warning("No data available for the selected filters.")
    
    st.divider()
    
    # ========================================================================
    # Critical Alerts
    # ========================================================================
    st.header("🚨 Critical Alerts")
    
    alerts_data = load_critical_alerts()
    
    if not alerts_data.empty:
        # Filter alerts based on sidebar selections
        if selected_location != 'All':
            alerts_data = alerts_data[alerts_data['LOCATION'] == selected_location]
        if selected_item != 'All':
            alerts_data = alerts_data[alerts_data['ITEM'] == selected_item]
        
        if not alerts_data.empty:
            for idx, alert in alerts_data.iterrows():
                status = alert['STOCK_STATUS']
                css_class = "critical-alert" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "warning-alert"
                
                st.markdown(f"""
                <div class="{css_class}">
                    <strong>{alert['ALERT_MESSAGE']}</strong><br>
                    📍 Location: {alert['LOCATION']} | 📦 Item: {alert['ITEM']}<br>
                    📊 Current Stock: {alert['CURRENT_STOCK']:.0f} | 📉 Avg Daily Usage: {alert['AVG_DAILY_USAGE']:.2f}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No critical alerts for the selected filters!")
    else:
        st.success("✅ No critical alerts - all stock levels are healthy!")
    
    st.divider()
    
    # ========================================================================
    # Location Summary
    # ========================================================================
    st.header("📍 Location Summary")
    
    location_data = load_location_summary()
    
    if not location_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart of status breakdown
            status_cols = ['OUT_OF_STOCK_COUNT', 'CRITICAL_COUNT', 'WARNING_COUNT', 'LOW_COUNT', 'HEALTHY_COUNT']
            status_data = location_data[['LOCATION'] + status_cols].set_index('LOCATION')
            
            fig = px.bar(
                status_data,
                barmode='stack',
                title="Stock Status Distribution by Location",
                labels={'value': 'Count', 'variable': 'Status'},
                color_discrete_map={
                    'OUT_OF_STOCK_COUNT': '#8B0000',
                    'CRITICAL_COUNT': '#DC143C',
                    'WARNING_COUNT': '#FFA500',
                    'LOW_COUNT': '#FFD700',
                    'HEALTHY_COUNT': '#32CD32'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Health score by location
            fig = px.bar(
                location_data,
                x='LOCATION',
                y='AVG_HEALTH_SCORE',
                title="Average Health Score by Location",
                color='AVG_HEALTH_SCORE',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ========================================================================
    # Procurement Recommendations
    # ========================================================================
    st.header("🛒 Procurement Recommendations")
    
    procurement_data = load_procurement_export()
    
    if not procurement_data.empty:
        # Filter based on selections
        if selected_location != 'All':
            procurement_data = procurement_data[procurement_data['Location'] == selected_location]
        if selected_item != 'All':
            procurement_data = procurement_data[procurement_data['Item Name'] == selected_item]
        
        if not procurement_data.empty:
            st.dataframe(procurement_data, use_container_width=True, height=300)
            
            # Download button
            csv = procurement_data.to_csv(index=False)
            st.download_button(
                label="📥 Download Procurement List (CSV)",
                data=csv,
                file_name=f"procurement_recommendations_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No procurement recommendations for the selected filters.")
    else:
        st.success("✅ No reorder recommendations needed at this time!")
    
    st.divider()
    
    # ========================================================================
    # Item Performance
    # ========================================================================
    st.header("📦 Item Performance Analysis")
    
    item_data = load_item_performance()
    
    if not item_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top items by usage
            top_items = item_data.nlargest(10, 'TOTAL_ISSUED_7DAYS')
            fig = px.bar(
                top_items,
                x='ITEM',
                y='TOTAL_ISSUED_7DAYS',
                title="Top 10 Items by Usage (Last 7 Days)",
                color='DEMAND_CATEGORY',
                color_discrete_map={
                    'HIGH_DEMAND': '#DC143C',
                    'NORMAL': '#FFA500',
                    'LOW_DEMAND': '#32CD32'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Items with critical locations
            critical_items = item_data[item_data['CRITICAL_LOCATIONS'] > 0].sort_values('CRITICAL_LOCATIONS', ascending=False)
            if not critical_items.empty:
                fig = px.bar(
                    critical_items.head(10),
                    x='ITEM',
                    y='CRITICAL_LOCATIONS',
                    title="Items with Most Critical Locations",
                    color='CRITICAL_LOCATIONS',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No items have critical locations!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>StockPulse 360 | Powered by Snowflake ❄️ | Built for AI for Good Hackathon</p>
        <p>Last Updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
