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
    
    # Header with SVG Snowflake icon
    snowflake_svg = get_svg_icon('snowflake', size=48, color="#29B5E8")
    st.markdown(f'''
    <div style="text-align: center; margin-bottom: 1rem;">
        <div style="display: inline-block; vertical-align: middle; margin-right: 15px;">
            {snowflake_svg}
        </div>
        <div class="main-header" style="display: inline-block; vertical-align: middle;">
            StockPulse 360
        </div>
    </div>
    <p class="subtitle">AI-Driven Stock Health Monitor | Powered by Snowflake</p>
    ''', unsafe_allow_html=True)
    
    st.divider()
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown(section_header("Navigation", "map"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation menu
        nav_options = [
            "Overview & Heatmap",
            "Critical Alerts",
            "Reorder Recommendations",
            "AI/ML Insights",
            "Advanced Analytics",
            "Supplier Management"
        ]
        
        selected_page = st.radio(
            "Select Section",
            nav_options,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Refresh button
        refresh_svg = get_svg_icon('refresh', size=18, color="#FFFFFF")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f'<div style="padding-top: 8px;">{refresh_svg}</div>', unsafe_allow_html=True)
        with col2:
            if st.button("Refresh Data", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        st.divider()
        
        # About section
        with st.expander("About StockPulse 360"):
            st.markdown("""
            **StockPulse 360** helps hospitals, ration shops, and NGOs:
            - Monitor stock health in real-time
            - Predict stock-outs early
            - Get reorder recommendations
            - Prevent waste and shortages
            """)
    
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
