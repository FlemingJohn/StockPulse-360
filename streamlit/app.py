"""
StockPulse 360 - Streamlit Dashboard (Modular Version)
Main application file with clean navigation structure
"""

import streamlit as st
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

# Store session in session_state for access by other modules
st.session_state['session'] = session

# Import modular components
from styles import CUSTOM_CSS
from utils import get_svg_icon, section_header
from pages import (
    render_overview_page,
    render_alerts_page,
    render_reorder_page,
    render_ai_ml_page,
    render_analytics_page,
    render_supplier_page
)

# ============================================================================
# Page Configuration
# ============================================================================
st.set_page_config(
    page_title="StockPulse 360",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point."""
    
    # Sidebar Navigation & Controls
    with st.sidebar:
        # 1. Premium Branding Header
        snowflake_svg = get_svg_icon('snowflake', size=32, color="#29B5E8")
        st.markdown(f'''
        <div class="sidebar-logo-container">
            {snowflake_svg}
            <span class="sidebar-logo-text">StockPulse 360</span>
        </div>
        ''', unsafe_allow_html=True)
        
        # 2. Navigation List (We need to know the page first to render filters above it)
        # However, to match the user request "fildes at top in side and nav in belwo", 
        # we'll use a placeholder for filters or render navigation after determining the page.
        
        nav_options = [
            "Overview & Heatmap",
            "Critical Alerts",
            "Reorder Recommendations",
            "AI/ML Insights",
            "Advanced Analytics",
            "Supplier Management"
        ]
        
        # We'll use a container for filters that will be populated by the pages
        filter_container = st.container()
        
        selected_page = st.radio(
            "Select Section",
            nav_options,
            label_visibility="collapsed"
        )
        
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
        
        st.spacer = st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # 3. Sidebar Footer
        st.markdown('---', unsafe_allow_html=True)
        refresh_svg = get_svg_icon('refresh', size=18, color="#FFFFFF")
        if st.button("Refresh System Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
            
        with st.expander("System Info"):
            st.markdown(f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")
            st.markdown("Version 1.0.1")

    # Store filter container in session state so pages can access it
    st.session_state['filter_container'] = filter_container
    
    # Main Content Area
    st.divider()
    
    # Conditional Page Rendering based on Navigation
    if selected_page == "Overview & Heatmap":
        render_overview_page()
    elif selected_page == "Critical Alerts":
        render_alerts_page()
    elif selected_page == "Reorder Recommendations":
        render_reorder_page()
    elif selected_page == "AI/ML Insights":
        render_ai_ml_page()
    elif selected_page == "Advanced Analytics":
        render_analytics_page()
    elif selected_page == "Supplier Management":
        render_supplier_page()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #0F4C81; padding: 2rem 0;">
        <p style="margin: 0;">
            Built with Snowflake | Last Updated: {}
        </p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
