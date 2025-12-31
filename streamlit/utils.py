"""
StockPulse 360 - Utility Functions
SVG icons, helpers, and data loading functions
"""

import streamlit as st
import pandas as pd

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
        
        'trophy': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 22h16" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10 14.66V17c0 .55.45 1 1 1h2c.55 0 1-.45 1-1v-2.34" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 2v12.5" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6 4v7a6 6 0 0 0 12 0V4" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'balance': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="12" y1="3" x2="12" y2="21" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="7" y1="13" x2="17" y2="13" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3 13c0 2.21 1.79 4 4 4s4-1.79 4-4" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13 13c0 2.21 1.79 4 4 4s4-1.79 4-4" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 3L7 13" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 3L17 13" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'calendar': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="16" y1="2" x2="16" y2="6" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="8" y1="2" x2="8" y2="6" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="3" y1="10" x2="21" y2="10" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'upload': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 8 12 3 7 8" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="3" x2="12" y2="15" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'download': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="7 10 12 15 17 10" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="15" x2="12" y2="3" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'check': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="20 6 9 17 4 12" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        
        'hourglass': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 22h14" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5 2h14" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M17 22v-4.17c0-.53-.21-1.04-.58-1.42L12 12l-4.42 4.41c-.37.38-.58.89-.58 1.42V22" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 2v4.17c0 .53.21 1.04.58 1.42L12 12l4.42-4.41c.37-.38.58-.89.58-1.42V2" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
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
# Data Loading Functions
# ============================================================================

def get_session():
    """Get Snowflake session from session_state or global."""
    # Try to get from session_state first
    if hasattr(st, 'session_state') and 'session' in st.session_state:
        return st.session_state['session']
    # Fallback: try to import and get session
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except:
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))
            from config import get_snowflake_session
            return get_snowflake_session()
        except Exception as e:
            st.error(f"Failed to connect to Snowflake: {e}")
            return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_stock_risk_data():
    """Load stock risk data from Snowflake."""
    session = get_session()
    if session:
        try:
            df = session.table("stock_risk").to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading stock_risk table: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_critical_alerts():
    """Load critical alerts."""
    session = get_session()
    if session:
        try:
            df = session.table("critical_alerts").to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading critical_alerts table: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_location_summary():
    """Load location summary."""
    session = get_session()
    if session:
        try:
            df = session.table("location_summary").to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading location_summary table: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_procurement_export():
    """Load procurement recommendations (formatted view)."""
    session = get_session()
    if session:
        try:
            df = session.table("procurement_export").to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading procurement_export view: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_reorder_recommendations():
    """Load raw reorder recommendations data."""
    session = get_session()
    if session:
        try:
            df = session.table("reorder_recommendations").to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading reorder_recommendations table: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_item_performance():
    """Load item performance data."""
    session = get_session()
    if session:
        try:
            df = session.table("item_performance").to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading item_performance table: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_seasonal_forecasts():
    """Load seasonal forecasts from AI/ML analysis."""
    session = get_session()
    if session:
        try:
            # Use lowercase table name (the one with data)
            df = session.sql('SELECT * FROM "seasonal_forecasts"').to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.warning(f"Seasonal forecasts not available: {e}")
            return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(ttl=300)
def load_abc_analysis():
    """Load ABC analysis data."""
    session = get_session()
    if session:
        try:
            df = session.sql('SELECT * FROM abc_analysis').to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.warning(f"ABC analysis not available: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_stockout_impact():
    """Load stockout impact analysis."""
    session = get_session()
    if session:
        try:
            df = session.sql('SELECT * FROM stockout_impact').to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.warning(f"Stockout impact not available: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_budget_tracking():
    """Load budget tracking data."""
    session = get_session()
    if session:
        try:
            df = session.sql('SELECT * FROM budget_tracking').to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.warning(f"Budget tracking not available: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_purchase_orders():
    """Load purchase orders."""
    session = get_session()
    if session:
        try:
            df = session.sql('SELECT * FROM purchase_orders').to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.warning(f"Purchase orders not available: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_supplier_performance():
    """Load supplier performance data."""
    session = get_session()
    if session:
        try:
            df = session.sql('SELECT * FROM supplier_performance').to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.warning(f"Supplier performance not available: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_supplier_comparison():
    """Load supplier comparison data."""
    session = get_session()
    if session:
        try:
            df = session.sql('SELECT * FROM supplier_comparison').to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.warning(f"Supplier comparison not available: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_supplier_cost_analysis():
    """Load supplier cost analysis data."""
    session = get_session()
    if session:
        try:
            df = session.sql('SELECT * FROM supplier_cost_analysis').to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.warning(f"Supplier cost analysis not available: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_delivery_schedule():
    """Load delivery schedule data."""
    session = get_session()
    if session:
        try:
            df = session.sql('SELECT * FROM delivery_schedule').to_pandas()
            df.columns = [c.upper() for c in df.columns]
            return df
        except Exception as e:
            st.warning(f"Delivery schedule not available: {e}")
            return pd.DataFrame()
    return pd.DataFrame()


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
