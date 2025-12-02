"""
StockPulse 360 - Utility Functions
SVG icons, helpers, and data loading functions
"""

import streamlit as st

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
# Data Loading Functions
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_stock_risk_data():
    """Load stock risk data from Snowflake."""
    from streamlit import session_state
    # Access session from main app
    session = st.session_state.get('session')
    if session:
        df = session.table("stock_risk").to_pandas()
        return df
    return None

@st.cache_data(ttl=300)
def load_critical_alerts():
    """Load critical alerts."""
    session = st.session_state.get('session')
    if session:
        df = session.table("critical_alerts").to_pandas()
        return df
    return None

@st.cache_data(ttl=300)
def load_location_summary():
    """Load location summary."""
    session = st.session_state.get('session')
    if session:
        df = session.table("location_summary").to_pandas()
        return df
    return None

@st.cache_data(ttl=300)
def load_procurement_export():
    """Load procurement recommendations."""
    session = st.session_state.get('session')
    if session:
        df = session.table("procurement_export").to_pandas()
        return df
    return None

@st.cache_data(ttl=300)
def load_item_performance():
    """Load item performance data."""
    session = st.session_state.get('session')
    if session:
        df = session.table("item_performance").to_pandas()
        return df
    return None

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
