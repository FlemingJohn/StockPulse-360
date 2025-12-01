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
# Custom CSS - Snowflake Theme
# ============================================================================
st.markdown("""
<style>
    /* Snowflake Color Palette */
    :root {
        --snowflake-blue: #29B5E8;
        --snowflake-dark-blue: #1E88E5;
        --snowflake-light-blue: #E3F2FD;
        --snowflake-navy: #0F4C81;
        --snowflake-gray: #F0F2F6;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #29B5E8 0%, #1E88E5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .subtitle {
        text-align: center;
        color: #0F4C81;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* SVG Icons */
    .icon-container {
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
    }
    
    .section-header-icon {
        display: inline-flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F2F6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #29B5E8;
        box-shadow: 0 2px 8px rgba(41, 181, 232, 0.1);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(41, 181, 232, 0.2);
    }
    
    /* Alert Cards */
    .critical-alert {
        background: linear-gradient(135deg, #FFF5F5 0%, #FFE6E6 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #DC143C;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 6px rgba(220, 20, 60, 0.1);
    }
    
    .warning-alert {
        background: linear-gradient(135deg, #FFFEF5 0%, #FFF4E6 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #FFA500;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 6px rgba(255, 165, 0, 0.1);
    }
    
    /* Buttons - Snowflake Style */
    .stButton>button {
        background: linear-gradient(135deg, #29B5E8 0%, #1E88E5 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 2px 6px rgba(41, 181, 232, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
        box-shadow: 0 4px 12px rgba(41, 181, 232, 0.4);
        transform: translateY(-1px);
    }
    
    /* Sidebar - Snowflake Theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F0F2F6 100%);
        border-right: 2px solid #29B5E8;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #F0F2F6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #0F4C81;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #29B5E8 0%, #1E88E5 100%);
        color: white;
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #0F4C81;
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #29B5E8;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Divider */
    hr {
        border-color: #29B5E8;
        opacity: 0.3;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #E3F2FD;
        border-left: 5px solid #29B5E8;
        border-radius: 8px;
    }
    
    .stSuccess {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
        border-radius: 8px;
    }
    
    .stWarning {
        background-color: #FFF4E6;
        border-left: 5px solid #FFA500;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SVG Icon Functions
# ============================================================================

def get_svg_icon(icon_name, size=24, color="#29B5E8"):
    """Get SVG icon by name."""
    icons = {
        'chart': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 3v18h18" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M18 9l-5 5-4-4-3 3" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'box': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="22.08" x2="12" y2="12" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'alert': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="9" x2="12" y2="13" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="17" x2="12.01" y2="17" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'location': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="10" r="3" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'cart': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="9" cy="21" r="1" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="20" cy="21" r="1" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'trending': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 6 23 6 23 12" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'map': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="8" y1="2" x2="8" y2="18" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="16" y1="6" x2="16" y2="22" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'snowflake': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="12" y1="2" x2="12" y2="22" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20 7l-8 5-8-5" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20 17l-8-5-8 5" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 7l8 5 8-5" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 17l8-5 8 5" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'settings': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="3" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 1v6m0 6v6m8.66-15l-3 5.2M6.34 15.8l-3 5.2m12.66 0l-3-5.2M6.34 8.2l-3-5.2" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'refresh': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="23 4 23 10 17 10" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'filter': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'info': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="16" x2="12" y2="12" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="8" x2="12.01" y2="8" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'dollar': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="12" y1="1" x2="12" y2="23" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
    }
    return icons.get(icon_name, '')

def section_header(title, icon_name):
    """Create a section header with icon."""
    icon_svg = get_svg_icon(icon_name, size=28, color="#29B5E8")
    return f'''
    <div class="section-header-icon">
        <span class="icon-container">{icon_svg}</span>
        <h2 style="color: #0F4C81; margin: 0; display: inline-block;">{title}</h2>
    </div>
    '''

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
    # Header with Snowflake branding
    st.markdown('<div class="main-header">❄️ StockPulse 360</div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Driven Stock Health Monitor | Powered by Snowflake</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.markdown(section_header("Dashboard Controls", "settings"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Refresh button with icon
        refresh_icon = get_svg_icon('refresh', size=20, color="#FFFFFF")
        if st.button(f"{refresh_icon} Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        
        # Filters
        st.markdown(section_header("Filters", "filter"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
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
        st.markdown(section_header("About", "info"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
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
    st.markdown(section_header("Key Metrics", "chart"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    st.markdown(section_header("Stock Health Heatmap", "map"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
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
                color_continuous_scale=[[0, '#DC143C'], [0.5, '#FFA500'], [1, '#29B5E8']],  # Snowflake colors
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
    st.markdown(section_header("Critical Alerts", "alert"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    st.markdown(section_header("Location Summary", "location"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    st.markdown(section_header("Procurement Recommendations", "cart"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    st.markdown(section_header("Item Performance Analysis", "trending"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    
    st.divider()
    
    # ========================================================================
    # Cost Optimization Dashboard
    # ========================================================================
    st.markdown(section_header("Cost Optimization & Budget Tracking", "box"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Load cost data
    try:
        budget_data = session.table("budget_tracking").to_pandas()
        savings_data = session.table("cost_savings_dashboard").to_pandas()
        cost_location_data = session.table("cost_per_location").to_pandas()
        roi_data = session.table("roi_analysis").to_pandas()
        
        # Budget Status Card
        if not budget_data.empty:
            budget_row = budget_data.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Monthly Budget",
                    f"₹{budget_row['MONTHLY_BUDGET']:,.0f}",
                    help="Total allocated budget for the month"
                )
            
            with col2:
                st.metric(
                    "Estimated Spend",
                    f"₹{budget_row['ESTIMATED_SPEND']:,.0f}",
                    delta=f"{budget_row['BUDGET_UTILIZATION_PCT']:.1f}%",
                    delta_color="inverse"
                )
            
            with col3:
                remaining = budget_row['REMAINING_BUDGET']
                delta_color = "normal" if remaining > 0 else "inverse"
                st.metric(
                    "Remaining Budget",
                    f"₹{abs(remaining):,.0f}",
                    delta="Over budget" if remaining < 0 else "Available",
                    delta_color=delta_color
                )
            
            with col4:
                status = budget_row['BUDGET_STATUS']
                status_emoji = {
                    'HEALTHY': '✅',
                    'MODERATE': '⚠️',
                    'WARNING': '🟠',
                    'OVER_BUDGET': '🔴'
                }.get(status, '❓')
                st.metric(
                    "Budget Status",
                    f"{status_emoji} {status}",
                    help="Current budget health status"
                )
            
            # Budget Alert
            if budget_row['BUDGET_STATUS'] == 'OVER_BUDGET':
                over_amount = abs(budget_row['REMAINING_BUDGET'])
                st.error(f"⚠️ **Budget Alert:** Procurement exceeds budget by ₹{over_amount:,.2f}")
            elif budget_row['BUDGET_STATUS'] == 'WARNING':
                st.warning(f"⚠️ **Warning:** Budget utilization at {budget_row['BUDGET_UTILIZATION_PCT']:.1f}%")
        
        st.divider()
        
        # Cost Savings & ROI
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Cost Savings Breakdown")
            
            if not savings_data.empty:
                # Create pie chart for savings
                fig = px.pie(
                    savings_data,
                    values='TOTAL_SAVINGS',
                    names='SAVINGS_CATEGORY',
                    title='Savings by Category',
                    color_discrete_sequence=['#29B5E8', '#1E88E5', '#1565C0']
                )
                fig.update_layout(
                    font=dict(family="Segoe UI", color="#0F4C81"),
                    plot_bgcolor='#FFFFFF',
                    paper_bgcolor='#F0F2F6'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Savings table
                st.dataframe(
                    savings_data[['SAVINGS_CATEGORY', 'TOTAL_SAVINGS', 'ITEMS_AFFECTED', 'DESCRIPTION']],
                    use_container_width=True,
                    hide_index=True
                )
                
                total_savings = savings_data['TOTAL_SAVINGS'].sum()
                st.success(f"✅ **Total Savings:** ₹{total_savings:,.2f}")
            else:
                st.info("No cost savings data available yet.")
        
        with col2:
            st.subheader("📊 Return on Investment (ROI)")
            
            if not roi_data.empty:
                roi_row = roi_data.iloc[0]
                
                # ROI Metrics
                st.metric(
                    "Total Procurement Cost",
                    f"₹{roi_row['TOTAL_PROCUREMENT_COST']:,.2f}",
                    help="Total cost of recommended orders"
                )
                
                st.metric(
                    "Total Value Generated",
                    f"₹{roi_row['TOTAL_VALUE_GENERATED']:,.2f}",
                    help="Savings + Stockout cost avoided"
                )
                
                st.metric(
                    "ROI Percentage",
                    f"{roi_row['ROI_PERCENTAGE']:.1f}%",
                    delta="Positive ROI" if roi_row['ROI_PERCENTAGE'] > 0 else "Negative ROI",
                    delta_color="normal" if roi_row['ROI_PERCENTAGE'] > 0 else "inverse"
                )
                
                # ROI Breakdown
                st.markdown("**Value Breakdown:**")
                st.write(f"- Cost Savings: ₹{roi_row['TOTAL_SAVINGS']:,.2f}")
                st.write(f"- Stockout Prevention: ₹{roi_row['STOCKOUT_COST_AVOIDED']:,.2f}")
                
                if roi_row['ROI_PERCENTAGE'] > 50:
                    st.success("🎉 Excellent ROI! System is highly effective.")
                elif roi_row['ROI_PERCENTAGE'] > 20:
                    st.info("✅ Good ROI. System is performing well.")
                else:
                    st.warning("⚠️ ROI could be improved.")
            else:
                st.info("ROI data not available yet.")
        
        st.divider()
        
        # Cost by Location
        st.subheader("📍 Procurement Cost by Location")
        
        if not cost_location_data.empty:
            # Bar chart
            fig = px.bar(
                cost_location_data,
                x='LOCATION',
                y='TOTAL_COST',
                title='Total Procurement Cost by Location',
                color='TOTAL_COST',
                color_continuous_scale=[[0, '#29B5E8'], [1, '#0F4C81']],
                labels={'TOTAL_COST': 'Total Cost (₹)'}
            )
            fig.update_layout(
                font=dict(family="Segoe UI", color="#0F4C81"),
                plot_bgcolor='#FFFFFF',
                paper_bgcolor='#F0F2F6'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed table
            st.dataframe(
                cost_location_data.style.format({
                    'TOTAL_COST': '₹{:,.2f}',
                    'AVG_ITEM_PRICE': '₹{:,.2f}',
                    'HIGHEST_COST_ITEM_VALUE': '₹{:,.2f}'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No cost data available by location.")
    
    except Exception as e:
        st.warning(f"⚠️ Cost optimization data not available. Please run the advanced_analytics.sql script first.")
        st.info("Run: `sql/advanced_analytics.sql` to enable cost tracking features.")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #F0F2F6 0%, #FFFFFF 100%); border-radius: 12px; margin-top: 2rem;">
        <p style="color: #0F4C81; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
            ❄️ StockPulse 360 | Powered by Snowflake
        </p>
        <p style="color: #29B5E8; font-size: 0.9rem; margin-bottom: 0.5rem;">
            Built for AI for Good Hackathon 🏆
        </p>
        <p style="color: #666; font-size: 0.85rem;">
            Last Updated: {}
        </p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
